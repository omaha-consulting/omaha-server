# Group Crash Reports

## Crash Report Collection [/api/crash_report/]

### List all Crash Reports [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            {
                "count": 209,
                "next": "http://omaha-server-dev.elasticbeanstalk.com/api/crash_report/?page=2",
                "previous": null,
                "results": [
                    {
                        "id": 1,
                        "upload_file_minidump": "https://example.com/minidump/2014/12/15/7b05e196-7e23-416b-bd13-99287924e214.dmp",
                        "archive": null,
                        "appid": "",
                        "userid": "",
                        "meta": null,
                        "signature": null,
                        "created": "2014-12-15T11:40:28.981640Z",
                        "modified": "2014-12-15T11:40:31.176896Z"
                    },
                    {
                        "id": 2,
                        "upload_file_minidump": "https://example.com/minidump/2014/12/15/7b05e196-7e23-416b-bd13-99287924e214.dmp",
                        "archive": null,
                        "appid": "",
                        "userid": "",
                        "meta": null,
                        "signature": null,
                        "created": "2014-12-15T11:50:52.581412Z",
                        "modified": "2014-12-15T11:50:53.097885Z"
                    }
                ]
            }

## Crash report [/api/crash_report/{id}/]

### Retrieve a Crash Report [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

        {
            "id": 1,
            "upload_file_minidump": "https://example.com/minidump/2014/12/15/7b05e196-7e23-416b-bd13-99287924e214.dmp",
            "archive": null,
            "appid": "",
            "userid": "",
            "meta": null,
            "signature": null,
            "created": "2014-12-15T11:40:28.981640Z",
            "modified": "2014-12-15T11:40:31.176896Z"
        }