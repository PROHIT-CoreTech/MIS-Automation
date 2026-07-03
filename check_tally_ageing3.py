"""Run: python check_tally_ageing3.py"""
import requests

TALLY_URL = "http://localhost:9000"

report_names = [
    "Bills Receivable",
    "Receivable",
    "Bills Receivables", 
    "Debtors",
    "Sundry Debtors",
    "Outstandings Receivable",
    "Outstanding",
    "Debtors Outstanding",
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
        resp = requests.post(TALLY_URL, data=xml_req.encode('utf-8'), timeout=10)
        xml = resp.text
        if 'LINEERROR' not in xml and len(xml) > 200:
            print(f"✅ FOUND: '{name}' — {len(xml)} chars")
            print(xml[:300])
        else:
            print(f"❌ '{name}'")
    except Exception as e:
        print(f"⏱️  '{name}' — Timeout/Error")

# Also fetch full Bills Payable to understand complete structure
print("\n\n=== BILLS PAYABLE — FULL STRUCTURE (first 2000 chars) ===")
xml_req2 = """<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>Bills Payable</REPORTNAME>
<STATICVARIABLES>
<SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY></ENVELOPE>"""
try:
    resp2 = requests.post(TALLY_URL, data=xml_req2.encode('utf-8'), timeout=15)
    print(resp2.text[:2000])
except Exception as e:
    print(f"Error: {e}")
