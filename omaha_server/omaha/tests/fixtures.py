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

request_update_check = b"""<?xml version="1.0" encoding="UTF-8"?>
<request protocol="3.0"
         version="1.3.23.0"
         ismachine="0"
         sessionid="{5FAD27D4-6BFA-4daa-A1B3-5A1F821FEE0F}"
         userid="{D0BBD725-742D-44ae-8D46-0231E881D58E}"
         installsource="scheduler"
         testsource="ossdev"
         requestid="{C8F6EDF3-B623-4ee6-B2DA-1D08A0B4C665}">
    <os platform="win" version="6.1" sp="" arch="x64"/>
    <app appid="{430FD4D0-B729-4F61-AA34-91526481799D}" version="1.2.23.0" nextversion="" lang="en" brand="GGLS"
         client="someclientid" installage="39">
        <updatecheck/>
        <ping r="1"/>
    </app>
    <app appid="{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}" version="2.2.2.0" nextversion="" lang="en" brand="GGLS"
         client="" installage="6">
        <updatecheck/>
        <ping r="1"/>
    </app>
</request>"""

request_event = b"""<?xml version="1.0" encoding="UTF-8"?>
<request protocol="3.0" version="1.3.23.0" ismachine="1" sessionid="{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}" userid="{D0BBD725-742D-44ae-8D46-0231E881D58E}" installsource="otherinstallcmd" testsource="ossdev" requestid="{164FC0EC-8EF7-42cb-A49D-474E20E8D352}">
  <os platform="win" version="6.1" sp="" arch="x64"/>
  <app appid="{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}" version="" nextversion="13.0.782.112" lang="en" brand="" client="" installage="6">
    <event eventtype="9" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="5" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="2" eventresult="4" errorcode="-2147219440" extracode1="268435463"/>
  </app>
</request>
"""

request_event_install_success = b"""<?xml version="1.0" encoding="UTF-8"?>
<request protocol="3.0" version="1.3.23.0" ismachine="1" sessionid="{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}" userid="{D0BBD725-742D-44ae-8D46-0231E881D58E}" installsource="otherinstallcmd" testsource="ossdev" requestid="{164FC0EC-8EF7-42cb-A49D-474E20E8D352}">
  <os platform="win" version="6.1" sp="" arch="x64"/>
  <app appid="{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}" version="" nextversion="0.0.0.1" lang="en" brand="" client="" installage="6">
    <event eventtype="9" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="5" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="2" eventresult="1" errorcode="0" extracode1="0"/>
  </app>
</request>
"""

request_event_update_success = b"""<?xml version="1.0" encoding="UTF-8"?>
<request protocol="3.0" version="1.3.23.0" ismachine="1" sessionid="{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}" userid="{D0BBD725-742D-44ae-8D46-0231E881D58E}" installsource="otherinstallcmd" testsource="ossdev" requestid="{164FC0EC-8EF7-42cb-A49D-474E20E8D352}">
  <os platform="win" version="6.1" sp="" arch="x64"/>
  <app appid="{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}" version="0.0.0.1" nextversion="0.0.0.2" lang="en" brand="" client="" installage="6">
    <event eventtype="9" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="5" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="3" eventresult="1" errorcode="0" extracode1="0"/>
  </app>
</request>
"""

request_event_uninstall_success = b"""<?xml version="1.0" encoding="UTF-8"?>
<request protocol="3.0" version="1.3.23.0" ismachine="1" sessionid="{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}" userid="{D0BBD725-742D-44ae-8D46-0231E881D58E}" installsource="otherinstallcmd" testsource="ossdev" requestid="{164FC0EC-8EF7-42cb-A49D-474E20E8D352}">
  <os platform="win" version="6.1" sp="" arch="x64"/>
  <app appid="{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}" version="0.0.0.2" nextversion="" lang="en" brand="" client="" installage="6">
    <event eventtype="9" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="5" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="4" eventresult="1" errorcode="0" extracode1="0"/>
  </app>
</request>
"""

request_data = b"""<?xml version="1.0" encoding="UTF-8"?>
<request protocol="3.0" version="1.3.23.0" ismachine="0" sessionid="{5FAD27D4-6BFA-4daa-A1B3-5A1F821FEE0F}" userid="{D0BBD725-742D-44ae-8D46-0231E881D58E}" installsource="scheduler" testsource="ossdev" requestid="{C8F6EDF3-B623-4ee6-B2DA-1D08A0B4C665}">
  <os platform="win" version="6.1" sp="" arch="x64"/>
  <app appid="{430FD4D0-B729-4F61-AA34-91526481799D}" version="1.3.23.0" nextversion="" lang="en" brand="GGLS" client="someclientid" installage="39">
    <updatecheck/>
    <data name="install" index="verboselogging"/>
    <data name="untrusted">Some untrusted data</data>
    <ping r="1"/>
  </app>
</request>"""

response_update_check_negative = b"""<?xml version="1.0" encoding="UTF-8"?>
<response protocol="3.0" server="prod">
  <daystart elapsed_seconds="56508" elapsed_days="2557"/>
  <app appid="{430FD4D0-B729-4F61-AA34-91526481799D}" status="ok">
    <updatecheck status="noupdate"/>
    <ping status="ok"/>
  </app>
  <app appid="{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}" status="ok">
    <updatecheck status="noupdate"/>
    <ping status="ok"/>
  </app>
</response>"""

response_update_check_positive = b"""<?xml version="1.0" encoding="UTF-8"?>
<response protocol="3.0" server="prod">
  <daystart elapsed_seconds="56508" elapsed_days="2557"/>
  <app appid="{430FD4D0-B729-4F61-AA34-91526481799D}" status="ok">
    <updatecheck status="noupdate"/>
    <ping status="ok"/>
  </app>
  <app appid="{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}" status="ok">
    <updatecheck status="ok">
      <urls>
        <url codebase="http://cache.pack.google.com/edgedl/chrome/install/782.112/"/>
      </urls>
      <manifest version="13.0.782.112">
        <packages>
          <package hash="VXriGUVI0TNqfLlU02vBel4Q3Zo=" name="chrome_installer.exe" required="true" size="23963192"/>
        </packages>
        <actions>
          <action arguments="--do-not-launch-chrome" event="install" run="chrome_installer.exe"/>
          <action version="13.0.782.112" event="postinstall" onsuccess="exitsilentlyonlaunchcmd"/>
        </actions>
      </manifest>
    </updatecheck>
    <ping status="ok"/>
  </app>
</response>"""

response_update_check_postitive_critical = b"""<?xml version="1.0" encoding="UTF-8"?>
<response protocol="3.0" server="prod">
  <daystart elapsed_seconds="56508" elapsed_days="2557"/>
  <app appid="{430FD4D0-B729-4F61-AA34-91526481799D}" status="ok">
    <updatecheck status="noupdate"/>
    <ping status="ok"/>
  </app>
  <app appid="{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}" status="ok">
    <updatecheck status="ok">
      <urls>
        <url codebase="http://cache.pack.google.com/edgedl/chrome/install/782.112/"/>
      </urls>
      <manifest version="13.0.782.111">
        <packages>
          <package hash="VXriGUVI0TNqfLlU02vBel4Q3Zo=" name="chrome_installer_critical.exe" required="true" size="23963192"/>
        </packages>
      </manifest>
    </updatecheck>
    <ping status="ok"/>
  </app>
</response>"""

response_event = b"""<?xml version="1.0" encoding="UTF-8"?>
<response protocol="3.0" server="prod">
  <daystart elapsed_seconds="56754" elapsed_days="2557"/>
  <app appid="{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}" status="ok">
    <event status="ok"/>
    <event status="ok"/>
    <event status="ok"/>
  </app>
</response>"""

response_data_doc = b"""<?xml version="1.0" encoding="UTF-8"?>
<response protocol="3.0" server="prod">
  <daystart elapsed_seconds="56754" elapsed_days="2557"/>
  <app appid="{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}" status="ok">
    <data index="verboselogging" name="install" status="ok">
      app-specific values here
    </data>
    <data name="untrusted" status="ok"/>
  </app>
</response>"""

response_data = b"""<?xml version="1.0" encoding="UTF-8"?>
<response protocol="3.0" server="prod">
  <daystart elapsed_seconds="56754" elapsed_days="2557"/>
  <app status="ok" appid="{430FD4D0-B729-4F61-AA34-91526481799D}">
    <data status="ok" index="verboselogging" name="install">app-specific values here</data>
    <data status="ok" name="untrusted"/>
    <updatecheck status="ok">
      <urls>
        <url codebase="http://cache.pack.google.com/edgedl/chrome/install/782.112/"/>
      </urls>
      <manifest version="13.0.782.112">
        <packages>
          <package hash="VXriGUVI0TNqfLlU02vBel4Q3Zo=" name="chrome_installer.exe" required="true" size="23963192"/>
        </packages>
      </manifest>
    </updatecheck>
    <ping status="ok"/>
  </app>
</response>"""

event_install_success = dict(eventtype="2", eventresult="1", errorcode="0", extracode1="0")
event_install_error = dict(eventtype="2", eventresult="0", errorcode="0", extracode1="0")
event_uninstall_success = dict(eventtype="4", eventresult="1", errorcode="0", extracode1="0")
