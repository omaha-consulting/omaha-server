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
                    "file": "https://example.com/sparkle/Installer/stable/Chromium-41.0.2224.0.dmg", 
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
                    "file": "https://example.com/sparkle/Installer/stable/Chromium-41.0.4444.0.dmg", 
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
            "file": "https://example.com/sparkle/Installer/stable/Chromium-41.0.4444.0.dmg", 
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
            "file": "https://example.com/sparkle/Installer/stable/Chromium-41.0.4444.0.dmg", 
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