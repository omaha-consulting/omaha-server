# Group Data

## Data Collection [/api/data{?id,app,index,name,value}/]

### List all Data [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            [
                {
                    "id": 2,
                    "app": "{DB77BFF7-8C02-4D31-A103-5FDE27CF6B3C}",
                    "index": "",
                    "name": 0,
                    "value": "Test",
                },
                {
                    "id": 1,
                    "app": "{DB77BFF7-8C02-4D31-A103-5FDE27CF6B3C}",
                    "index": "qwerty",
                    "name": 1,
                    "value": "",
                }
            ]

### Create an Data [POST]

+ Parameters
    * app (required, string, `{DB77BFF7-8C02-4D31-A103-5FDE27CF6B3C}`) ... App ID
    * name (required, number, `1`) ... Type of data. install=0, untrusted=1
    * index (optional, string, ``) 
    * value (optional, string, ``) 

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "app": {DB77BFF7-8C02-4D31-A103-5FDE27CF6B3C},
                "name": 1
            }

+ Response 201

        {
            "id": 9,
            "app": "{DB77BFF7-8C02-4D31-A103-5FDE27CF6B3C}",
            "index": "",
            "name": 1,
            "value": "",
        }

## Data [/api/data/{id}/]

+ Parameters
    * id (required, number, `42`)

### Retrieve a Data [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

        {
            "id": 9,
            "app": "{DB77BFF7-8C02-4D31-A103-5FDE27CF6B3C}",
            "index": null,
            "name": 1,
            "value": "",
        }

### Patch a Data [PATCH]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "name": 0
            }

+ Response 200 (application/json)

        {
            "id": 9,
            "app": "{DB77BFF7-8C02-4D31-A103-5FDE27CF6B3C}",
            "index": null,
            "name": 0,
            "value": "",
        }

### Update a Data [PUT]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "app": {DB77BFF7-8C02-4D31-A103-5FDE27CF6B3C},
                "name": 0
            }

+ Response 200 (application/json)

        {
            "id": 9,
            "app": "{DB77BFF7-8C02-4D31-A103-5FDE27CF6B3C}",
            "index": null,
            "name": 0,
            "value": "",
        }

### Remove a Data [DELETE]

+ Request

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 204