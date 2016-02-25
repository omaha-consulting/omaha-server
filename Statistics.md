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
