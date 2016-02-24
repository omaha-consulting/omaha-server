# Group Feedbacks

## Feedback Collection [/api/feedback/]

### List all Feedbacks [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)
    + Body

            {
                "count": 120,
                "next": "http://omaha-server-dev.elasticbeanstalk.com/api/feedback/?page=2",
                "previous": null,
                "results": [
                    {
                        "id": 1,
                        "created": "2015-07-06T08:27:48.436166Z",
                        "modified": "2015-07-06T08:27:49.432753Z",
                        "screenshot": null,
                        "blackbox": "https://example.com/blackbox/2015/7/6/34b33907-82b8-4643-819a-7111b6ae0959/blackbox.tar",
                        "system_logs": null,
                        "attached_file": null,
                        "feedback_data": {
                            "blackbox": {
                                "data": "[binary content]",
                                "mime_type": "application/octet-stream"
                            },
                            "product_id": 237,
                            "chrome_data": {
                              "chrome_browser_data": {
                                    "category": "OTHER"
                                },
                                "chrome_platform": "CHROME_BROWSER"
                            },
                            "type_id": 0,
                            "web_data": {
                                "url": "",
                                "navigator": {
                                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.0 Safari/537.36"
                                }
                            },
                            "common_data": {
                                "gaia_id": 0,
                                "source_description_language": "en-US",
                                "description": "The blackbox test requested",
                                "user_email": ""
                            }
                        }
                    },
                    {
                        "id": 2,
                        "created": "2015-07-06T09:23:48.789477Z",
                        "modified": "2015-07-06T09:23:49.866857Z",
                        "screenshot": "https://example.com/screenshot/2015/7/6/5c2449d6-c268-4ba8-8d8c-efc9cb39bf88/screenshot.png",
                        "blackbox": "https://example.com/blackbox/2015/7/6/f4c793a2-8692-49c6-83ae-d5d505682f15/blackbox.tar",
                        "system_logs": "https://example.com/system_logs/2015/7/6/240658e7-6552-4bb8-89f4-ed28bbe53153/system_logs.zip",
                        "attached_file": "https://example.com/feedback_attach/2015/7/6/bda32309-ccef-4ab9-b7ab-2dd5905bebae/noname.zip",
                        "feedback_data": {
                            "blackbox": {
                                "data": "[binary content]",
                                "mime_type": "application/octet-stream"
                            },
                            "screenshot": {
                                "binary_content": "[binary content]",
                                "dimensions": {
                                    "width": 0.0,
                                    "height": 0.0
                                },
                                "mime_type": "image/png"
                            },
                            "chrome_data": {
                                "chrome_browser_data": {
                                    "category": "OTHER"
                                },
                                "chrome_platform": "CHROME_BROWSER"
                            },
                            "type_id": 0,
                            "product_specific_binary_data": [
                                {
                                    "data": "[binary content]",
                                    "name": "system_logs.zip",
                                    "mime_type": "application/octet-stream"
                                },
                                {
                                    "data": "[binary content]",
                                    "name": "noname.zip",
                                    "mime_type": "application/octet-stream"
                                }
                            ],
                            "web_data": {
                                "url": "chrome://newtab/",
                                "navigator": {
                                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.0 Safari/537.36"
                                },
                                "product_specific_data": [
                                    {
                                        "key": "CHROME VERSION",
                                        "value": "42.0.2311.0 (Developer Build 1733f6e8da766bf7e5b364979bd123e9602746c9 Mac OS X)"
                                    },
                                    {
                                        "key": "OS VERSION",
                                        "value": "Mac OS X: 10.10.3"
                                    },
                                    {
                                        "key": "data_reduction_proxy",
                                        "value": "disabled"
                                    },
                                    {
                                        "key": "extensions",
                                        "value": "Google Slides,\nWeb Store,\nGoogle Docs,\nGoogle Drive,\nYouTube,\nGoogle Search,\nBookmark Manager,\nSettings,\nGoogle Sheets,\nFeedback,\nCryptoTokenExtension,\nCloud Print,\nPDF Viewer,\nGoogle Wallet,\nGoogle Now,\nGmail\n"
                                    },
                                    {
                                        "key": "mem_usage",
                                        "value": "Browser 185 MB private, 0 MB shared\nExtension [Feedback|Feedback] 174 MB private, 0 MB shared\nTab [New Tab] 110 MB private, 0 MB shared\nGPU [] 86 MB private, 0 MB shared\n"
                                    }
                                ]
                            },
                            "common_data": {
                                "gaia_id": 0,
                                "source_description_language": "en-US",
                                "description": "Issue description",
                                "user_email": "user@example.com"
                            },
                            "product_id": 237
                        }
                    }
                ]
            }

## Feedback [/api/feedback/{id}/]

### Retrieve a Feedback [GET]

+ Request (application/json)

    + Headers

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

        {
            "id": 1,
            "created": "2015-07-06T08:27:48.436166Z",
            "modified": "2015-07-06T08:27:49.432753Z",
            "screenshot": null,
            "blackbox": "https://example.com/blackbox/2015/7/6/34b33907-82b8-4643-819a-7111b6ae0959/blackbox.tar",
            "system_logs": null,
            "attached_file": null,
            "feedback_data": {
                "blackbox": {
                    "data": "[binary content]",
                    "mime_type": "application/octet-stream"
                },
                "product_id": 237,
                "chrome_data": {
                    "chrome_browser_data": {
                        "category": "OTHER"
                    },
                    "chrome_platform": "CHROME_BROWSER"
                },
                "type_id": 0,
                "web_data": {
                    "url": "",
                    "navigator": {
                        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.0 Safari/537.36"
                    }
                },
                "common_data": {
                    "gaia_id": 0,
                    "source_description_language": "en-US",
                    "description": "The blackbox test requested",
                    "user_email": ""
                }
            }
        }