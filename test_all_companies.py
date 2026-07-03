"""
Test - Fetch ALL companies from Tally Prime
Multiple approaches to find working one
"""
import requests
import re

TALLY_URL = "http://localhost:9000"

# Approach 1: TDL with ISALTERED flag to get all companies
xml1 = """<ENVELOPE>
<HEADER>
<VERSION>1</VERSION>
<TALLYREQUEST>Export</TALLYREQUEST>
<TYPE>Data</TYPE>
<ID>AllCompanies</ID>
</HEADER>
<BODY><DESC><TDL><TDLMESSAGE>
<REPORT NAME="AllCompanies">
<FORMS>CompForm</FORMS>
</REPORT>
<FORM NAME="CompForm">
<PARTS>CompPart</PARTS>
</FORM>
<PART NAME="CompPart">
<LINES>CompLine</LINES>
<REPEAT>CompLine : CompCollection</REPEAT>
<SCROLLED>Vertical</SCROLLED>
</PART>
<LINE NAME="CompLine">
<FIELDS>CompName</FIELDS>
</LINE>
<FIELD NAME="CompName">
<SET>$Name</SET>
</FIELD>
<COLLECTION NAME="CompCollection" ISINITIALIZE="Yes">
<TYPE>Company</TYPE>
<BELONGSTO>##SVCURRENTCOMPANY</BELONGSTO>
</COLLECTION>
</TDLMESSAGE></TDL></DESC></BODY></ENVELOPE>"""

# Approach 2: Without BELONGSTO filter
xml2 = """<ENVELOPE>
<HEADER>
<VERSION>1</VERSION>
<TALLYREQUEST>Export</TALLYREQUEST>
<TYPE>Data</TYPE>
<ID>AllCo2</ID>
</HEADER>
<BODY><DESC><TDL><TDLMESSAGE>
<REPORT NAME="AllCo2">
<FORMS>F2</FORMS>
</REPORT>
<FORM NAME="F2"><PARTS>P2</PARTS></FORM>
<PART NAME="P2">
<LINES>L2</LINES>
<REPEAT>L2 : AllCoList</REPEAT>
<SCROLLED>Vertical</SCROLLED>
</PART>
<LINE NAME="L2"><FIELDS>F2Name,F2Path</FIELDS></LINE>
<FIELD NAME="F2Name"><SET>$Name</SET></FIELD>
<FIELD NAME="F2Path"><SET>$DataPath</SET></FIELD>
<COLLECTION NAME="AllCoList" ISINITIALIZE="Yes">
<TYPE>Company</TYPE>
<FETCH>Name,DataPath,StartingFrom</FETCH>
</COLLECTION>
</TDLMESSAGE></TDL></DESC></BODY></ENVELOPE>"""

# Approach 3: Get companies with StartingFrom date
xml3 = """<ENVELOPE>
<HEADER>
<VERSION>1</VERSION>
<TALLYREQUEST>Export</TALLYREQUEST>
<TYPE>Data</TYPE>
<ID>CoWithDate</ID>
</HEADER>
<BODY><DESC><TDL><TDLMESSAGE>
<REPORT NAME="CoWithDate">
<FORMS>FDate</FORMS>
</REPORT>
<FORM NAME="FDate"><PARTS>PDate</PARTS></FORM>
<PART NAME="PDate">
<LINES>LDate</LINES>
<REPEAT>LDate : CoDateList</REPEAT>
<SCROLLED>Vertical</SCROLLED>
</PART>
<LINE NAME="LDate"><FIELDS>FDName,FDFrom</FIELDS></LINE>
<FIELD NAME="FDName"><SET>$Name</SET></FIELD>
<FIELD NAME="FDFrom"><SET>$StartingFrom</SET></FIELD>
<COLLECTION NAME="CoDateList" ISINITIALIZE="Yes">
<TYPE>Company</TYPE>
<FETCH>Name,StartingFrom</FETCH>
</COLLECTION>
</TDLMESSAGE></TDL></DESC></BODY></ENVELOPE>"""

for name, xml in [
    ("All Companies (with BELONGSTO)", xml1),
    ("All Companies (with DataPath)", xml2),
    ("All Companies (with StartingFrom)", xml3),
]:
    try:
        r = requests.post(TALLY_URL, data=xml.encode('utf-8'),
                         headers={'Content-Type':'application/xml'}, timeout=20)
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"FULL RESPONSE:\n{r.text[:2000]}")

        # Try to extract names
        names = re.findall(r'<(?:F2NAME|FDNAME|COMPNAME|MYFIELD|NAME)>(.*?)</(?:F2NAME|FDNAME|COMPNAME|MYFIELD|NAME)>', r.text)
        if names:
            print(f"\nExtracted names ({len(names)}): {names[:10]}")
    except Exception as e:
        print(f"ERROR: {e}")
