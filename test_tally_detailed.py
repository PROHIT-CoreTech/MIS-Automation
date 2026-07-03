"""
Test detailed Tally XML with date range and company name
to understand exact format for parsing
"""
import requests
from datetime import datetime

TALLY_URL = "http://localhost:9000"

# Test 1: P&L with date range (no company specified = current open company)
xml1 = """<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>Profit and Loss</REPORTNAME>
<STATICVARIABLES>
<SVFROMDATE>20250401</SVFROMDATE>
<SVTODATE>20251231</SVTODATE>
<EXPLODEFLAG>Yes</EXPLODEFLAG>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY>
</ENVELOPE>"""

# Test 2: Get current company name via TDL
xml2 = """<ENVELOPE>
<HEADER>
<VERSION>1</VERSION>
<TALLYREQUEST>Export</TALLYREQUEST>
<TYPE>Data</TYPE>
<ID>MyReport</ID>
</HEADER>
<BODY>
<DESC>
<TDL><TDLMESSAGE>
<REPORT NAME="MyReport">
<FORMS>MyForm</FORMS>
</REPORT>
<FORM NAME="MyForm">
<PARTS>MyPart</PARTS>
</FORM>
<PART NAME="MyPart">
<LINES>MyLine</LINES>
<REPEAT>MyLine : MyCollection</REPEAT>
<SCROLLED>Vertical</SCROLLED>
</PART>
<LINE NAME="MyLine">
<FIELDS>MyField</FIELDS>
</LINE>
<FIELD NAME="MyField">
<SET>$Name</SET>
</FIELD>
<COLLECTION NAME="MyCollection" ISINITIALIZE="Yes">
<TYPE>Company</TYPE>
</COLLECTION>
</TDLMESSAGE></TDL>
</DESC>
</BODY>
</ENVELOPE>"""

# Test 3: Ledger collection
xml3 = """<ENVELOPE>
<HEADER>
<VERSION>1</VERSION>
<TALLYREQUEST>Export</TALLYREQUEST>
<TYPE>Collection</TYPE>
<ID>LedList</ID>
</HEADER>
<BODY>
<DESC>
<TDL><TDLMESSAGE>
<COLLECTION NAME="LedList">
<TYPE>Ledger</TYPE>
<FETCH>Name,Parent,OpeningBalance,ClosingBalance</FETCH>
</COLLECTION>
</TDLMESSAGE></TDL>
</DESC>
</BODY>
</ENVELOPE>"""

for name, xml in [
    ("P&L with date range (FULL)", xml1),
    ("Company name via TDL", xml2),
    ("Ledger collection", xml3),
]:
    try:
        r = requests.post(TALLY_URL, data=xml.encode('utf-8'),
                         headers={'Content-Type':'application/xml'}, timeout=20)
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"RESPONSE (first 1000 chars):\n{r.text[:1000]}")
    except Exception as e:
        print(f"ERROR: {e}")
