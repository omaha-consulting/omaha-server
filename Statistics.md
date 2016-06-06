# Group Statistics

## Users by months for app [/api/statistics/months/{app_name}{?start,end}]

### Get statistics [GET]

+ Parameters
    * app_name (required, string, `AppTest`)
    * start (optional, string, `2015-02`) ... Range start in the "YYYY-MM" format
    * end (optional, string, `2016-02`) ... Range start in the "YYYY-MM" format

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            {
                "data": {
                    "win": {
                        "new": [
                            [
                                "2015-02",
                                9
                            ],
                            [
                                "2015-03",
                                12
                            ],
                            [
                                "2015-04",
                                6
                            ],
                            [
                                "2015-05",
                                8
                            ],
                            [
                                "2015-06",
                                9
                            ],
                            [
                                "2015-07",
                                13
                            ],
                            [
                                "2015-08",
                                7
                            ],
                            [
                                "2015-09",
                                12
                            ],
                            [
                                "2015-10",
                                11
                            ],
                            [
                                "2015-11",
                                7
                            ],
                            [
                                "2015-12",
                                7
                            ],
                            [
                                "2016-01",
                                6
                            ],
                            [
                                "2016-02",
                                10
                            ]
                        ],

                        "uninstalls": [
                            [
                                "2015-02",
                                6
                            ],
                            [
                                "2015-03",
                                3
                            ],
                            [
                                "2015-04",
                                1
                            ],
                            [
                                "2015-05",
                                2
                            ],
                            [
                                "2015-06",
                                5
                            ],
                            [
                                "2015-07",
                                4
                            ],
                            [
                                "2015-08",
                                6
                            ],
                            [
                                "2015-09",
                                2
                            ],
                            [
                                "2015-10",
                                1
                            ],
                            [
                                "2015-11",
                                0
                            ],
                            [
                                "2015-12",
                                3
                            ],
                            [
                                "2016-01",
                                11
                            ],
                            [
                                "2016-02",
                                8
                            ]
                        ],
                        "updates": [
                            [
                                "2015-02",
                                42
                            ],
                            [
                                "2015-03",
                                34
                            ],
                            [
                                "2015-04",
                                49
                            ],
                            [
                                "2015-05",
                                39
                            ],
                            [
                                "2015-06",
                                34
                            ],
                            [
                                "2015-07",
                                35
                            ],
                            [
                                "2015-08",
                                39
                            ],
                            [
                                "2015-09",
                                40
                            ],
                            [
                                "2015-10",
                                36
                            ],
                            [
                                "2015-11",
                                38
                            ],
                            [
                                "2015-12",
                                35
                            ],
                            [
                                "2016-01",
                                28
                            ],
                            [
                                "2016-02",
                                41
                            ]
                        ]
                    },
                    "mac": {
                        "new": [
                            [
                                "2015-02",
                                10
                            ],
                            [
                                "2015-03",
                                11
                            ],
                            [
                                "2015-04",
                                7
                            ],
                            [
                                "2015-05",
                                8
                            ],
                            [
                                "2015-06",
                                11
                            ],
                            [
                                "2015-07",
                                8
                            ],
                            [
                                "2015-08",
                                9
                            ],
                            [
                                "2015-09",
                                5
                            ],
                            [
                                "2015-10",
                                8
                            ],
                            [
                                "2015-11",
                                7
                            ],
                            [
                                "2015-12",
                                6
                            ],
                            [
                                "2016-01",
                                7
                            ],
                            [
                                "2016-02",
                                9
                            ]
                        ],
                        "updates": [
                            [
                                "2015-02",
                                8
                            ],
                            [
                                "2015-03",
                                12
                            ],
                            [
                                "2015-04",
                                12
                            ],
                            [
                                "2015-05",
                                9
                            ],
                            [
                                "2015-06",
                                11
                            ],
                            [
                                "2015-07",
                                8
                            ],
                            [
                                "2015-08",
                                14
                            ],
                            [
                                "2015-09",
                                16
                            ],
                            [
                                "2015-10",
                                6
                            ],
                            [
                                "2015-11",
                                14
                            ],
                            [
                                "2015-12",
                                11
                            ],
                            [
                                "2016-01",
                                10
                            ],
                            [
                                "2016-02",
                                16
                            ]
                        ]
                    }
                }
            }

## Users by versions for app [/api/statistics/version/{app_name}{?date}]

### Get statistics [GET]

+ Parameters
    * app_name (required, string, `AppTest`)
    * date (optional, string, `2016-02`) ... Month in the "YYYY-MM" format
    
+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            {
                "data": {
                    "win": {
                        "38.0.0.42": 19,
                        "38.0.0.55": 21,
                        "39.5.0.0": 22
                    },
                    "mac": {
                        "38.0.0.42": 36
                    }
                }
            }

## Users by channels for app [/api/statistics/channels/{app_name}{?date}]

### Get statistics [GET]

+ Parameters
    * app_name (required, string, `AppTest`)
    * date (optional, string, `2016-02`) ... Month in the "YYYY-MM" format


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
