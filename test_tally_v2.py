"""Test Tally - after opening a company"""
import requests

TALLY_URL = "http://localhost:9000"

tests = [
    ("Current Company Name", """<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>Company Info</REPORTNAME>
</REQUESTDESC></EXPORTDATA></BODY>
</ENVELOPE>"""),

    ("TDL Company Collection with FETCH", """<ENVELOPE>
<HEADER>
<VERSION>1</VERSION>
<TALLYREQUEST>Export</TALLYREQUEST>
<TYPE>Collection</TYPE>
<ID>CompList</ID>
</HEADER>
<BODY>
<DESC>
<TDL><TDLMESSAGE>
<COLLECTION NAME="CompList" ISINITIALIZE="Yes">
<TYPE>Company</TYPE>
<FETCH>Name</FETCH>
<FETCH>STARTINGFROM</FETCH>
<FETCH>ENDINGAT</FETCH>
</COLLECTION>
</TDLMESSAGE></TDL>
</DESC>
</BODY>
</ENVELOPE>"""),

    ("Simple Balance Sheet", """<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>Balance Sheet</REPORTNAME>
</REQUESTDESC></EXPORTDATA></BODY>
</ENVELOPE>"""),

    ("Profit Loss", """<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>Profit and Loss</REPORTNAME>
</REQUESTDESC></EXPORTDATA></BODY>
</ENVELOPE>"""),
]

for name, xml in tests:
    try:
        r = requests.post(TALLY_URL, data=xml.encode('utf-8'),
                         headers={'Content-Type':'application/xml'}, timeout=15)
        print(f"\n{'='*55}")
        print(f"TEST: {name}")
        print(f"RESPONSE (first 600 chars):\n{r.text[:600]}")
    except Exception as e:
        print(f"ERROR: {e}")
