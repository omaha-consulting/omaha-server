# Group Downloads Portal
API returns an information about the latest versions of applications available on the server. The information contains supported platforms, provided channels, version numbers and download links.

## Latest Available Versions [/api]

### Get Latest Versions [GET]

+ Request (application/json)
    
    + Headers
    
            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==
            
+ Response 200 (application/json)
    
    + Body
              
            {
                "OtherApp": {
                    "win": {
                        "stable": {
                            "url": "https://bucket.s3.amazonaws.com/build/OtherApp/stable/win/9.9.9.9/OtherApp_acctest_initial.exe",
                            "version": "9.9.9.9"
                        }
                    }
                },
                "TestApp": {
                    "win": {
                        "acctest": {
                            "url": "https://bucket.s3.amazonaws.com/build/TestApp/acctest/win/47.0.2526.112/mini_installer.exe",
                            "version": "47.0.2526.113"
                        },
                        "stable": {
                            "url": "https://bucket.s3.amazonaws.com/build/TestApp/stable/win/0.0.0.42/installer.exe",
                            "version": "0.0.0.42"
                        }
                    },
                    "mac": {
                        "alpha": {
                            "url": "https://bucket.s3.amazonaws.com/sparkle/TestApp/alpha/2526.113/TestApp.dmg",
                            "version": "47.0.2526.113"
                        }
                    }
                }
            }