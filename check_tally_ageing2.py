"""Run: python check_tally_ageing2.py"""
import requests

TALLY_URL = "http://localhost:9000"

# Try different report names for Tally Prime
report_names = [
    "Outstandings",
    "Outstanding Receivables", 
    "Outstanding Payables",
    "Ageing Analysis",
    "Bills Receivable",
    "Bills Payable",
    "Receivables",
    "Payables",
    "Statement of Accounts",
    "Ledger",
]

for name in report_names:
    xml_req = f"""<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>{name}</REPORTNAME>
<STATICVARIABLES>
<SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY></ENVELOPE>"""

    try:
        resp = requests.post(TALLY_URL, data=xml_req.encode('utf-8'), timeout=5)
        xml = resp.text
        if 'LINEERROR' not in xml and len(xml) > 200:
            print(f"✅ FOUND: '{name}' — {len(xml)} chars")
            print(xml[:500])
            print("...")
        else:
            print(f"❌ '{name}' — {xml[:80].strip()}")
    except Exception as e:
        print(f"❌ '{name}' — Error: {e}")
