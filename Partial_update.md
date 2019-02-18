# Group Partial Update

## Partial update Collection [/api/partialupdate{?version,is_enabled,percent,start_date,end_date,exclude_new_users,active_users}]

### List all Partial Updates [GET]


+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            [
                {
                    "id": 1,
                    "version": 128,
                    "is_enabled": false,
                    "percent": 50.0,
                    "start_date": "2018-03-07",
                    "end_date": "2018-03-07",
                    "exclude_new_users": false,
                    "active_users": 1
                }
            ]

### Create a Partial Update [POST]

+ Parameters
    * version (required, number, `12`) ... Version ID
    * is_enabled = `false` (optional, boolean, `true`)
    * percent (required, string, `50`) ... Sets a percentage of users to which the version will be distributed.
    * start_date (required, string, `\"2018-03-07\"`) ... Is a commencement of a rolling out
    * end_date (required, string, `\"2018-03-07\"`) ... Is a date when a partial update ends and the version won't be distributed.
    * exclude_new_users (optional, boolean, `true`) ... If it has the enabled value, the version will be distributed to only existing users.
    * active_users (optional, number, `1`) ... A rule sets active users which we’ll roll out the version to.

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "version": 128,
                "percent": 50.0,
                "start_date": "2018-03-07",
                "end_date": "2018-03-07"
            }

+ Response 201

        {
            "id": 1,
            "version": 128,
            "is_enabled": false,
            "percent": 50.0,
            "start_date": "2018-03-07",
            "end_date": "2018-03-07",
            "exclude_new_users": false,
            "active_users": 1
        }

## Partial Update [/api/partialupdate/{id}/]

+ Parameters
    * id (required, number, `42`)


### Retrieve a Partial Update [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

        {
            "id": 42,
            "version": 128,
            "is_enabled": false,
            "percent": 50.0,
            "start_date": "2018-03-07",
            "end_date": "2018-03-07",
            "exclude_new_users": false,
            "active_users": 1
        }


### Patch a Partial Update [PATCH]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "is_enabled": true,
            }

+ Response 200 (application/json)

        {
            "id": 1,
            "version": 128,
            "is_enabled": true,
            "percent": 50.0,
            "start_date": "2018-03-07",
            "end_date": "2018-03-07",
            "exclude_new_users": false,
            "active_users": 1
        }

### Update a Partial Update [PUT]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

    + Body

            {
                "is_enabled": true,
                "version": 128,
                "percent": 50.0,
                "start_date": "2018-03-07",
                "end_date": "2018-03-07"
            }

+ Response 200 (application/json)

        {
            "id": 1,
            "version": 128,
            "is_enabled": true,
            "percent": 50.0,
            "start_date": "2018-03-07",
            "end_date": "2018-03-07",
            "exclude_new_users": false,
            "active_users": 1
        }

### Remove a Partial Update [DELETE]

+ Request

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 204