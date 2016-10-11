# Group Channel

## Channel Collection [/api/channel{?name}/]

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

## Channel [/api/channel/{id}/]

+ Parameters
    * id (required, number, `42`)

### Retrieve a Channel [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

        {
            "id": 11,
            "name": "dev",
        }

### Patch a Channel [PATCH]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "name": "beta",
            }

+ Response 200 (application/json)

        {
            "id": 11,
            "name": "beta",
        }

### Update a Channel [PUT]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "name": "beta",
            }

+ Response 200 (application/json)

        {
            "id": 11,
            "name": "beta",
        }

### Remove a Channel [DELETE]

+ Request

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 204