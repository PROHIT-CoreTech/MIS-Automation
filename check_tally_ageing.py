"""
Run: python check_tally_ageing.py
Fetches Tally Outstanding Receivables/Payables XML structure
"""
import requests

TALLY_URL = "http://localhost:9000"

for report_type, ledger_type in [
    ("Outstanding Receivables", "Sundry Debtors"),
    ("Outstanding Payables",    "Sundry Creditors"),
]:
    xml_req = f"""<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>Bills Outstanding</REPORTNAME>
<STATICVARIABLES>
<SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
<EXPLODEFLAG>Yes</EXPLODEFLAG>
<LEDGERTYPENAME>{ledger_type}</LEDGERTYPENAME>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY></ENVELOPE>"""

    try:
        resp = requests.post(TALLY_URL, data=xml_req.encode('utf-8'), timeout=15)
        xml = resp.text
        print(f"\n{'='*60}")
        print(f"REPORT: {report_type}")
        print(f"Response length: {len(xml)} chars")
        print(f"\nFirst 3000 chars:")
        print(xml[:3000])
    except Exception as e:
        print(f"Error: {e}")
