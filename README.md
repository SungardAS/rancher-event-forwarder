# Rancher Event Forwarder

## Summary

This is an app to send rancher events to AWS SNS topic.
Currently, it only sends the events whose type is 'name.change' and resource_type is 'environment'

## Input Parameters

* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* AWS_SESSION_TOKEN
* AWS_REGION
* CATTLE_URL
* CATTLE_ACCESS_KEY
* CATTLE_SECRET_KEY
* SNS_TOPIC_ARN
* WEBSOCKET_TRACE : true/false

## License
Apache-2.0 ©
