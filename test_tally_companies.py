"""
Test different Tally XML requests to find correct company list format
"""
import requests

TALLY_URL = "http://localhost:9000"

# Try different approaches
requests_to_try = [
    ("Collection of Companies", """<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<STATICVARIABLES><SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT></STATICVARIABLES>
<REQUESTOBJECTS>
<COLLECTION ISINITIALIZE="Yes">
<TYPE>Company</TYPE>
<FETCH>Name</FETCH>
</COLLECTION>
</REQUESTOBJECTS>
</REQUESTDESC></EXPORTDATA></BODY>
</ENVELOPE>"""),

    ("TDL Collection", """<ENVELOPE>
<HEADER>
<VERSION>1</VERSION>
<TALLYREQUEST>Export</TALLYREQUEST>
<TYPE>Collection</TYPE>
<ID>MyCompanies</ID>
</HEADER>
<BODY>
<DESC>
<TDL>
<TDLMESSAGE>
<COLLECTION NAME="MyCompanies" ISINITIALIZE="Yes">
<TYPE>Company</TYPE>
<FETCH>Name,StartingFrom</FETCH>
</COLLECTION>
</TDLMESSAGE>
</TDL>
</DESC>
</BODY>
</ENVELOPE>"""),

    ("GetLicense", """<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>GetLicenseInfo</REPORTNAME>
</REQUESTDESC></EXPORTDATA></BODY>
</ENVELOPE>"""),
]

for name, xml in requests_to_try:
    try:
        r = requests.post(TALLY_URL, data=xml.encode('utf-8'),
                         headers={'Content-Type':'application/xml'}, timeout=10)
        print(f"\n{'='*50}")
        print(f"REQUEST: {name}")
        print(f"RESPONSE:\n{r.text[:500]}")
    except Exception as e:
        print(f"ERROR: {e}")
