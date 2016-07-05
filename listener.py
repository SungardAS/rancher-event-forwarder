
# https://github.com/mediadepot/docker-rancher-events/blob/master/listener.py

import websocket
import base64
import os
import json
import boto3

def connect_dynamodb():
    dynamodb = boto3.client(
        'dynamodb',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.environ.get('AWS_SESSION_TOKEN'),
        region_name=os.environ.get('AWS_REGION')
    )
    return dynamodb


def save_dynamodb(resource_name, resource_state):
    dynamodb = connect_dynamodb()
    table_name = "charreada_mgmt_systems"
    res = dynamodb.query(
        TableName=table_name,
        KeyConditionExpression="id = :id",
        ExpressionAttributeValues={ ":id": {"S": resource_name} })
    item = res['Items'][0]
    item['status']['S'] = resource_state
    dynamodb.put_item(TableName=table_name, Item=item)
    print "state has been successfully updated"


def connect_sns():
    sns = boto3.client(
        'sns',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.environ.get('AWS_SESSION_TOKEN'),
        region_name=os.environ.get('AWS_REGION')
    )
    return sns


def publish_to_sns(resource):
    sns = connect_sns()
    sns.publish(
        TopicArn=os.environ.get('SNS_TOPIC_ARN'),
        Message=json.dumps(resource),
        Subject='resource.change'
    )
    print 'a message is published to sns'


def on_message(ws, message):
    msg_json = json.loads(message)
    type = msg_json.get('type')
    name = msg_json.get('name')
    if name == "resource.change":
        try:
            resource_type = msg_json.get('data').get('resource').get('type')
            resource_name = msg_json.get('data').get('resource').get('name')
            resource_state = msg_json.get('data').get('resource').get('state')
            if resource_type == "environment":
                print "%s:%s:%s" % (resource_type, resource_name, resource_state)
                #save_dynamodb(resource_name, resource_state)
                publish_to_sns(msg_json.get('data').get('resource'))
        except:
            pass


def on_error(ws, error):
    raise Exception('Received websocket error: [%s]', error)


def on_close(ws):
    print '### Websocket connection closed ###'


def on_open(ws):
    print '### Websocket connection opened ###'


if __name__ == "__main__":

    # retrieve api endpoint, access key and secret from environmental variables.
    api_endpoint = os.getenv('CATTLE_URL').replace('http:', 'ws:').replace('https:', 'wss:')
    access_key = os.getenv('CATTLE_ACCESS_KEY')
    secret_key = os.getenv('CATTLE_SECRET_KEY')
    auth_header = 'Authorization: Basic ' + base64.standard_b64encode(access_key + ':' + secret_key).encode(
        'latin1').strip()

    headers = []
    headers.append(auth_header)

    trace = os.getenv('WEBSOCKET_TRACE') == "false"
    websocket.enableTrace(not trace)
    print 'websocket trace is set to be %s' % (not trace)
    ws = websocket.WebSocketApp(api_endpoint + '/subscribe?eventNames=resource.change',
                                header=headers,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)
    print 'start listening to rancher manager websocket'
    ws.run_forever()
