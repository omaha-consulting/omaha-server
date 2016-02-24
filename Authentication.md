# omaha-server API

# Authentication

Omaha-server allows REST clients to authenicate themselves with a user name and password using [basic authentication](http://en.wikipedia.org/wiki/Basic_access_authentication).

## Simple example

Most client software provides a simple mechanism for supplying a user name and password and will build the required authentication headers automatically. For example you can specify the -u argument with curl as follows

    curl -D- -u username:password -X GET -H "Content-Type: application/json" http://example.com/api/omaha/version

## Supplying Basic Auth headers

If you need to you may construct and send basic auth headers yourself. To do this you need to perform the following steps:

1. Build a string of the form username:password
2. Base64 encode the string 
3. Supply an "Authorization" header with content "Basic " followed by the encoded string. For example, the string `username:password` encodes to `dXNlcm5hbWU6cGFzc3dvcmQ=` in base64, so you would make the request as follows.


    curl -D- -X GET -H "Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=" -H "Content-Type: application/json" "http://example.com/api/omaha/version"