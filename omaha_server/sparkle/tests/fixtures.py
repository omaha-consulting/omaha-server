# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2014 Crystalnix Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
"""

response_sparkle = b"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <channel>
        <title>chrome</title>
        <link>http://example.com/sparkle/chrome/stable/appcast.xml</link>
        <description>Most recent changes with links to updates.</description>
        <language>en</language>

            <item>
                <title>chrome 782.112</title>
                <description><![CDATA[

                ]]>
                </description>
                <pubDate>Tue, 14 Oct 2014 08:28:05 +0000</pubDate>
                <enclosure url="http://cache.pack.google.com/edgedl/chrome/install/782.112/sparkle/chrome/stable/782.112/chrome.dmg"
                           sparkle:version="782.112"
                           sparkle:shortVersionString="13.0.782.112"
                           length="23963192" type="application/octet-stream"/>
            </item>

    </channel>
</rss>"""

response_sparkle_with_dsa = b"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <channel>
        <title>chrome_dsa</title>
        <link>http://example.com/sparkle/chrome_dsa/stable/appcast.xml</link>
        <description>Most recent changes with links to updates.</description>
        <language>en</language>

            <item>
                <title>chrome_dsa 782.112</title>
                <description><![CDATA[

                ]]>
                </description>
                <pubDate>Tue, 14 Oct 2014 08:28:05 +0000</pubDate>
                <enclosure url="http://cache.pack.google.com/edgedl/chrome/install/782.112/sparkle/chrome_dsa/stable/782.112/chrome.dmg"
                           sparkle:version="782.112"
                           sparkle:shortVersionString="13.0.782.112"
                           sparkle:dsaSignature="MCwCFCdoW13VBGJWIfIklKxQVyetgxE7AhQTVuY9uQT0KOV1UEk21epBsGZMPg=="
                           length="23963192" type="application/octet-stream"/>
            </item>

    </channel>
</rss>"""
