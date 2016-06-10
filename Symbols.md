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

## Symbols [/api/symbols/{id}/]

+ Parameters
    * id (required, number, `42`)

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