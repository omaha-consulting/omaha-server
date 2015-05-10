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

## Applications Collection [/api/app{?id,name}]

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

# Group Platform

## Platform Collection [/api/platform{?name}]

### List all Platforms [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            [
                {
                    "id": 1, 
                    "name": "win"
                }, 
                {
                    "id": 2, 
                    "name": "mac"
                }
            ]

### Create a Platform [POST]

+ Parameters
    * name (required, string, `ios`)

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "name": "ios",
            }

+ Response 201

        {
            "id": 3,
            "name": "ios",
        }

## Platform [/api/platform/{id}]

### Retrieve a Platform [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

        {
            "id": 1,
            "name": "win",
        }

### Remove a Platform [DELETE]

+ Request

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 204

# Group Channel

## Channel Collection [/api/channel{?name}]

### List all Channels [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            [
                {
                    "id": 1, 
                    "name": "stable"
                }, 
                {
                    "id": 2, 
                    "name": "beta"
                }, 
                {
                    "id": 3, 
                    "name": "alpha"
                }
            ]

### Create a Channel [POST]

+ Parameters
    * name (required, string, `dev`)

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "name": "dev",
            }

+ Response 201

        {
            "id": 11,
            "name": "dev",
        }

## Channel [/api/channel/{id}]

### Retrieve a Channel [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

        {
            "id": 11,
            "name": "dev",
        }

### Remove a Channel [DELETE]

+ Request

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 204

# Group Omaha Version

## Version List [/api/omaha/version{?is_enabled,app,channel,platform,release_notes,file}]

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

# Group Action

## Actions Collection [/api/action{?id,version,event,run,arguments,successurl,terminateallbrowsers,successsaction,other}]

### List all Actions [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            [
                {
                    "id": 1, 
                    "version": 6, 
                    "event": 1, 
                    "run": "", 
                    "arguments": "--do-not-launch-chrome", 
                    "successurl": "", 
                    "terminateallbrowsers": false, 
                    "successsaction": "default", 
                    "other": null
                }, 
                {
                    "id": 3, 
                    "version": 8, 
                    "event": 1, 
                    "run": "", 
                    "arguments": "--do-not-launch-chrome", 
                    "successurl": "", 
                    "terminateallbrowsers": false, 
                    "successsaction": "default", 
                    "other": null
                }
            ]

### Create a Action [POST]

+ Parameters
    * id (required, string, `{8A76FC95-0086-4BCE-9517-DC09DDB5652F}`)
    * version (required, number, `12`) ... Version ID
    * event (required, number, `1`) ... Contains a fixed string denoting when this action should be run. preinstall=0, install=1, postinstall=2, update=3
    * run (optional, string) The name of an installer binary to run.
    * arguments = `--do-not-launch-chrome` (optional, string) Arguments to be passed to that installer binary.
    * successurl (optional, string) A URL to be opened using the system's default web browser on a successful install.
    * terminateallbrowsers = `false` (optional, boolean, `true`) If "true", close all browser windows before starting the installer binary.
    * successsaction = `default` (optional, string) Contains a fixed string denoting some action to take in response to a successful install.
    * other (optional, dict) Other attributes

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "version": 7,
                "event": 1
            }

+ Response 201

        {
            "id": 11, 
            "version": 7, 
            "event": 1, 
            "run": "", 
            "arguments": "--do-not-launch-chrome", 
            "successurl": "", 
            "terminateallbrowsers": false, 
            "successsaction": "default", 
            "other": null
        }

## Action [/api/action/{id}]

### Retrieve a Action [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

        {
            "id": 11, 
            "version": 7, 
            "event": 1, 
            "run": "", 
            "arguments": "--do-not-launch-chrome", 
            "successurl": "", 
            "terminateallbrowsers": false, 
            "successsaction": "default", 
            "other": null
        }

### Remove a Action [DELETE]

+ Request

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 204

# Group Sparkle Version

## Version List [/api/sparkle/version{?app,channel,release_notes,file,dsa_signature,version,short_version}]

### Get versions [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            [
                {
                    "id": 1, 
                    "app": "{43C257D5-533D-462C-8166-E276519687DE}", 
                    "channel": 5, 
                    "version": "2224.0", 
                    "short_version": "41.0.2224.0", 
                    "release_notes": "", 
                    "file": "https://example.com/sparkle/SparrowInstaller/stable/Chromium-41.0.2224.0.dmg", 
                    "file_size": 66241209, 
                    "dsa_signature": "MCwCFDb2CcPI9BI9DErZtT2cR0v18Er2AhQe8l2UChvQS596Sxn/lZ694oE1Vg==", 
                    "created": "2015-01-13T08:52:18.176934Z", 
                    "modified": "2015-01-14T08:52:36.732462Z"
                }, 
                {
                    "id": 3, 
                    "app": "{43C257D5-533D-462C-8166-E276519687DE}", 
                    "channel": 5, 
                    "version": "4444.0", 
                    "short_version": "41.0.4444.0", 
                    "release_notes": "<p>Version 41.0.4444.0 is out now</p>", 
                    "file": "https://example.com/sparkle/SparrowInstaller/stable/Chromium-41.0.4444.0.dmg", 
                    "file_size": 66243223, 
                    "dsa_signature": "MCwCFFjHuSSd/QKCuIJsl7T2GDQd1NeZAhRqnZqXoFdpbfzyaE772N0TISwFzQ==", 
                    "created": "2015-01-14T10:50:56.019360Z", 
                    "modified": "2015-01-14T10:50:56.026884Z"
                }
            ]


### Create a Version [POST]

+ Parameters

    * app (required, number, `12`) ... Application ID
    * channel (required, number, `2`) ... Channel ID
    * version (required, string, `2592.123`)
    * short_version (optional, string, `30.0.2592.123`)
    * dsa_signature (optional, string, `MCwCFFjHuSSd/QKCuIJsl7T2GDQd1NeZAhRqnZqXoFdpbfzyaE772N0TISwFzQ==`)
    * release_notes (optional, string, `Release notes`)
    * file (required, file)

+ Request (multipart/form-data)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

                {
                    "app": "{43C257D5-533D-462C-8166-E276519687DE}", 
                    "channel": 5, 
                    "version": "4444.0", 
                    "short_version": "41.0.4444.0", 
                    "release_notes": "<p>Version 41.0.4444.0 is out now</p>", 
                    "file": "{FILE}", 
                    "dsa_signature": "MCwCFFjHuSSd/QKCuIJsl7T2GDQd1NeZAhRqnZqXoFdpbfzyaE772N0TISwFzQ=="
                }

+ Response 201

        {
            "id": 3, 
            "app": "{43C257D5-533D-462C-8166-E276519687DE}", 
            "channel": 5, 
            "version": "4444.0", 
            "short_version": "41.0.4444.0", 
            "release_notes": "<p>Version 41.0.4444.0 is out now</p>", 
            "file": "https://example.com/sparkle/SparrowInstaller/stable/Chromium-41.0.4444.0.dmg", 
            "file_size": 66243223, 
            "dsa_signature": "MCwCFFjHuSSd/QKCuIJsl7T2GDQd1NeZAhRqnZqXoFdpbfzyaE772N0TISwFzQ==", 
            "created": "2015-01-14T10:50:56.019360Z", 
            "modified": "2015-01-14T10:50:56.026884Z"
        }

## Version [/api/sparkle/version/{id}]

### Retrieve a Version [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

        {
            "id": 3, 
            "app": "{43C257D5-533D-462C-8166-E276519687DE}", 
            "channel": 5, 
            "version": "4444.0", 
            "short_version": "41.0.4444.0", 
            "release_notes": "<p>Version 41.0.4444.0 is out now</p>", 
            "file": "https://example.com/sparkle/SparrowInstaller/stable/Chromium-41.0.4444.0.dmg", 
            "file_size": 66243223, 
            "dsa_signature": "MCwCFFjHuSSd/QKCuIJsl7T2GDQd1NeZAhRqnZqXoFdpbfzyaE772N0TISwFzQ==", 
            "created": "2015-01-14T10:50:56.019360Z", 
            "modified": "2015-01-14T10:50:56.026884Z"
        }

### Remove a Version [DELETE]

+ Request

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 204

# Group Symbols

## Symbols List [/api/symbols{?file}]

### Get Symbols [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            [
                {
                    "id": 1, 
                    "file": "https://example.com/symbols/BreakpadTestApp.pdb/C1C0FA629EAA4B4D9DD2ADE270A231CC1/BreakpadTestApp.sym", 
                    "debug_id": "C1C0FA629EAA4B4D9DD2ADE270A231CC1", 
                    "debug_file": "BreakpadTestApp.pdb", 
                    "created": "2014-12-15T11:40:12.832711Z", 
                    "modified": "2014-12-15T11:40:12.837032Z"
                }, 
                {
                    "id": 3, 
                    "file": "https://example.com/symbols/goopdate_unsigned.pdb/C5D54208325A45FA8CDEB66A3FE6A9F61/goopdate_unsigned.sym", 
                    "debug_id": "C5D54208325A45FA8CDEB66A3FE6A9F61", 
                    "debug_file": "goopdate_unsigned.pdb", 
                    "created": "2014-12-23T10:36:26.930401Z", 
                    "modified": "2014-12-26T08:05:11.377844Z"
                }
            ]


### Create a Symbols [POST]

+ Parameters

    * file (required, file)

+ Request (multipart/form-data)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

                {
                    "file": "{FILE}"
                }

+ Response 201

        {
            "id": 3, 
            "file": "https://example.com/symbols/goopdate_unsigned.pdb/C5D54208325A45FA8CDEB66A3FE6A9F61/goopdate_unsigned.sym", 
            "debug_id": "C5D54208325A45FA8CDEB66A3FE6A9F61", 
            "debug_file": "goopdate_unsigned.pdb", 
            "created": "2014-12-23T10:36:26.930401Z", 
            "modified": "2014-12-26T08:05:11.377844Z"
        }

## Symbols [/api/symbols/{id}]

### Retrieve a Symbols [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

        {
            "id": 3, 
            "file": "https://example.com/symbols/goopdate_unsigned.pdb/C5D54208325A45FA8CDEB66A3FE6A9F61/goopdate_unsigned.sym", 
            "debug_id": "C5D54208325A45FA8CDEB66A3FE6A9F61", 
            "debug_file": "goopdate_unsigned.pdb", 
            "created": "2014-12-23T10:36:26.930401Z", 
            "modified": "2014-12-26T08:05:11.377844Z"
        }

### Remove a Symbols [DELETE]

+ Request

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 204

# Group Statistics

## Users by months [/api/statistics/months]

### Get overall statistics [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            {
                "data": {
                    "February": 251, 
                    "October": 235, 
                    "March": 260, 
                    "August": 256, 
                    "April": 255, 
                    "May": 269, 
                    "January": 249, 
                    "June": 239, 
                    "September": 235, 
                    "December": 255, 
                    "July": 265, 
                    "November": 231
                }
            }

## Users by months for app [/api/statistics/months/{app_name}/]

### Get statistics [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            {
                "data": {
                    "February": 251, 
                    "October": 235, 
                    "March": 260, 
                    "August": 256, 
                    "April": 255, 
                    "May": 269, 
                    "January": 249, 
                    "June": 239, 
                    "September": 235, 
                    "December": 255, 
                    "July": 265, 
                    "November": 231
                }
            }

## Users by versions for app [/api/statistics/version/{app_name}/]

### Get statistics [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            {
                "data": {
                    "39.0.2171.2": 1230, 
                    "0.0.1.0": 0, 
                    "39.0.2171.1": 2140, 
                    "38.0.2125.2": 320
                }
            }

## Users by channels for app [/api/statistics/channels/{app_name}/]

### Get statistics [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            {
                "data": {
                    "dev": 1230, 
                    "alpha": 0, 
                    "release": 2140
                }
            }

# Group Omaha server

## Version [/api/version]

### Get version [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            {
                "version": "0.0.6"
            }
            