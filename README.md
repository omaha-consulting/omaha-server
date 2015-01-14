FORMAT: 1A

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


# Group Application

## Applications Collection [/api/app]

### List all Applications [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            [
                {
                    "id": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}",
                    "name": "Chromium"
                },
                {
                    "id": "{430FD4D0-B729-4F61-AA34-91526481799D}",
                    "name": "Potato"
                }
            ]

### Create a Application [POST]

+ Parameters
    * id (required, string, `{8A76FC95-0086-4BCE-9517-DC09DDB5652F}`)
    * name (required, string, `Chromium`)

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "id": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}",
                "name": "Chromium",
            }

+ Response 201

        {
            "id": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}",
            "name": "Chromium",
        }

## Application [/api/app/{id}]

### Retrieve a Application [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

        {
            "id": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}",
            "name": "Chromium",
        }

### Remove a Application [DELETE]

+ Request

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 204

# Group Omaha Version

## Version List [/api/omaha/version]

### Get versions [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            [
                {
                    "id": 33, 
                    "is_enabled": true, 
                    "app": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}", 
                    "platform": 1, 
                    "channel": 1, 
                    "version": "1.0.0.0", 
                    "release_notes": "", 
                    "file": "https://example.com/build/UpdateTestApp/stable/win/UpdateTestAppInstaller.1.0.0.0.exe", 
                    "file_hash": "kYSewtBIGUdgDZ1TXaf2WhFQ8Og=", 
                    "file_size": 143974, 
                    "created": "2014-11-28T11:17:52.952931Z", 
                    "modified": "2014-12-18T08:59:58.394326Z"
                }, 
                {
                    "id": 38, 
                    "is_enabled": true, 
                    "app": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}", 
                    "platform": 1, 
                    "channel": 2, 
                    "version": "2.0.0.1024", 
                    "release_notes": "", 
                    "file": "https://example.com/build/UpdateTestApp/beta/win/UpdateTestAppInstaller.2.0.0.1024.beta.exe", 
                    "file_hash": "u8QB8baBHs45RmKNCTIGGtNHXbc=", 
                    "file_size": 143963, 
                    "created": "2014-11-28T11:25:37.213001Z", 
                    "modified": "2014-12-18T09:00:00.094911Z"
                }
            ]


### Create a Version [POST]

+ Parameters

    * is_enabled = `true` (optional, boolean, `false`)
    * app (required, number, `12`) ... Application ID
    * platform (required, number, `1`) ... Platform ID
    * channel (required, number, `2`) ... Channel ID
    * version (required, string, `30.0.2592.123`)
    * release_notes (optional, string, `Release notes`)
    * file (required, file)

+ Request (multipart/form-data)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

                {
                    "app": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}", 
                    "platform": 1, 
                    "channel": 2, 
                    "version": "2.0.0.1024", 
                    "file": "File", 
                    "file_hash": "u8QB8baBHs45RmKNCTIGGtNHXbc=", 
                    "file_size": 143963, 
                    "created": "2014-11-28T11:25:37.213001Z", 
                    "modified": "2014-12-18T09:00:00.094911Z"
                }

+ Response 201

            {
                "id": 38, 
                "is_enabled": true, 
                "app": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}", 
                "platform": 1, 
                "channel": 2, 
                "version": "2.0.0.1024", 
                "release_notes": "", 
                "file": "https://example.com/build/UpdateTestApp/beta/win/UpdateTestAppInstaller.2.0.0.1024.beta.exe", 
                "file_hash": "u8QB8baBHs45RmKNCTIGGtNHXbc=", 
                "file_size": 143963, 
                "created": "2014-11-28T11:25:37.213001Z", 
                "modified": "2014-12-18T09:00:00.094911Z"
            }

## Version [/api/omaha/version/{id}]

### Retrieve a Version [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

        {
            "id": 38, 
            "is_enabled": true, 
            "app": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}", 
            "platform": 1, 
            "channel": 2, 
            "version": "2.0.0.1024", 
            "release_notes": "", 
            "file": "https://example.com/build/UpdateTestApp/beta/win/UpdateTestAppInstaller.2.0.0.1024.beta.exe", 
            "file_hash": "u8QB8baBHs45RmKNCTIGGtNHXbc=", 
            "file_size": 143963, 
            "created": "2014-11-28T11:25:37.213001Z", 
            "modified": "2014-12-18T09:00:00.094911Z"
        }

### Remove a Version [DELETE]

+ Request

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 204