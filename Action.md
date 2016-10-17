# Group Action

## Actions Collection [/api/action{?id,version,event,run,arguments,successurl,terminateallbrowsers,successsaction,other}/]

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

### Create an Action [POST]

+ Parameters
    * version (required, number, `12`) ... Version ID
    * event (required, number, `1`) ... Contains a fixed string denoting when this action should be run. preinstall=0, install=1, postinstall=2, update=3
    * run (optional, string, ``) ... The name of an installer binary to run.
    * arguments = `--do-not-launch-chrome` (optional, string) ... Arguments to be passed to that installer binary.
    * successurl (optional, string, ``) ... A URL to be opened using the system's default web browser on a successful install.
    * terminateallbrowsers = `false` (optional, boolean, `true`) ... If "true", close all browser windows before starting the installer binary.
    * successsaction = `default` (optional, string) ... Contains a fixed string denoting some action to take in response to a successful install.
    * other (optional, dict, ``) ... Other attributes

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

## Action [/api/action/{id}/]

+ Parameters
    * id (required, number, `42`)

### Retrieve an Action [GET]

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

### Patch an Action [PATCH]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "event": 0
            }

+ Response 200 (application/json)

        {
            "id": 11,
            "version": 7,
            "event": 0,
            "run": "",
            "arguments": "--do-not-launch-chrome",
            "successurl": "",
            "terminateallbrowsers": false,
            "successsaction": "default",
            "other": null
        }

### Update an Action [PUT]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "version": 7,
                "event": 0
            }

+ Response 200 (application/json)

        {
            "id": 11,
            "version": 7,
            "event": 0,
            "run": "",
            "arguments": "--do-not-launch-chrome",
            "successurl": "",
            "terminateallbrowsers": false,
            "successsaction": "default",
            "other": null
        }

### Remove an Action [DELETE]

+ Request

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 204