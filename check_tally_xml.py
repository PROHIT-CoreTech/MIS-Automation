"""
Run: python check_tally_xml.py
Fetches raw Tally XML for one month and shows COGS structure
"""
import requests, re
from datetime import date

TALLY_URL = "http://localhost:9000"

# Fetch Apr-25
xml_req = """<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>Profit and Loss</REPORTNAME>
<STATICVARIABLES>
<SVFROMDATE>20250401</SVFROMDATE>
<SVTODATE>20250430</SVTODATE>
<SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY></ENVELOPE>"""

try:
    resp = requests.post(TALLY_URL, data=xml_req.encode('utf-8'), timeout=10)
    xml = resp.text
    
    # Find COGS related section
    lines = xml.split('\n')
    in_cogs = False
    for i, line in enumerate(lines):
        if any(x in line.upper() for x in ['PURCHASE', 'OPENING', 'CLOSING', 
                                             'COST OF SALES', 'DIRECT EXP']):
            in_cogs = True
        if in_cogs:
            print(f"{i:4d}: {line.rstrip()}")
            if i > 0 and in_cogs and len([l for l in lines[max(0,i-20):i+1] 
                                          if any(x in l.upper() for x in 
                                          ['PURCHASE','OPENING','CLOSING'])]) > 15:
                break
                
except Exception as e:
    print(f"Error connecting to Tally: {e}")
    print("Make sure Tally is open with a company loaded on port 9000")
