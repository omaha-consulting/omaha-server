# Group Omaha Version

## Version List [/api/omaha/version{?is_enabled,app,channel,platform,release_notes,file}/]

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

## Version [/api/omaha/version/{id}/]

+ Parameters
    * id (required, number, `42`)

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

### Patch a Version [PATCH]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

                {
                    "is_enabled": false,
                }

+ Response 200 (application/json)

        {
            "id": 38,
            "is_enabled": false,
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

### Update a Version [PUT]

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
                    "is_enabled": false,
                }

+ Response 200 (application/json)

        {
            "id": 38,
            "is_enabled": false,
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