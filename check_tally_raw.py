"""
Run: python check_tally_raw.py
Fetches raw Tally XML and shows FULL structure to find Purchase/Opening Stock
"""
import requests, sys

TALLY_URL = "http://localhost:9000"

# Try Apr-25
xml_req = """<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>Profit and Loss</REPORTNAME>
<STATICVARIABLES>
<SVFROMDATE>20250401</SVFROMDATE>
<SVTODATE>20250430</SVTODATE>
<SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
<EXPLODEFLAG>Yes</EXPLODEFLAG>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY></ENVELOPE>"""

try:
    resp = requests.post(TALLY_URL, data=xml_req.encode('utf-8'), timeout=15)
    xml  = resp.text
    
    print(f"Response length: {len(xml)} chars")
    print()
    
    # Find Purchase/Opening Stock sections
    lines = xml.split('\n')
    keywords = ['purchase', 'opening', 'closing', 'salary', 'wages', 'epfo', 'esic']
    
    print("=== LINES CONTAINING KEY WORDS ===")
    for i, line in enumerate(lines):
        ll = line.lower()
        if any(k in ll for k in keywords):
            # Print context
            start = max(0, i-1)
            end   = min(len(lines), i+3)
            for j in range(start, end):
                print(f"  {j:4d}: {lines[j].rstrip()}")
            print()
            
except Exception as e:
    print(f"Error: {e}")
    print("Make sure Tally is open with USP company loaded on port 9000")
