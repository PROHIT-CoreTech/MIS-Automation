"""Run: python check_tally_company.py
Check current active company in Tally and how to switch
"""
import requests
TALLY_URL = "http://localhost:9000"

# Get current company list
xml_req = """<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>List of Companies</REPORTNAME>
<STATICVARIABLES>
<SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY></ENVELOPE>"""

try:
    resp = requests.post(TALLY_URL, data=xml_req.encode('utf-8'), timeout=10)
    print("Company List Response:")
    print(resp.text[:2000])
except Exception as e:
    print(f"Error: {e}")

# Try with SVCURRENTCOMPANY
print("\n\n=== Try fetching Bills Receivable with company name ===")
for company in ["Unique Steel Products", "Intellichemie Industries LLP"]:
    xml_req2 = f"""<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>Bills Receivable</REPORTNAME>
<STATICVARIABLES>
<SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
<SVCURRENTCOMPANY>{company}</SVCURRENTCOMPANY>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY></ENVELOPE>"""
    try:
        resp2 = requests.post(TALLY_URL, data=xml_req2.encode('utf-8'), timeout=10)
        xml = resp2.text
        bill_count = xml.count('<BILLOVERDUE>')
        print(f"  '{company}': {bill_count} bills, {len(xml)} chars")
        if bill_count > 0:
            print(f"  First 300: {xml[:300]}")
    except Exception as e:
        print(f"  Error: {e}")
