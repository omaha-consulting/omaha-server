# Group Platform

## Platform Collection [/api/platform{?name}/]

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

## Platform [/api/platform/{id}/]

+ Parameters
    * id (required, number, `42`)

### Retrieve a Platform [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

        {
            "id": 1,
            "name": "win",
        }

### Patch a Platform [PATCH]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "name": "ios",
            }

+ Response 200 (application/json)

        {
            "id": 1,
            "name": "ios",
        }

### Update a Platform [PUT]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "name": "ios",
            }

+ Response 200 (application/json)

        {
            "id": 1,
            "name": "ios",
        }

### Remove a Platform [DELETE]

+ Request

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 204