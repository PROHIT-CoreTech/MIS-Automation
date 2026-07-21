"""
Tally Prime HTTP API — Tested & Working
Format: DSPDISPNAME + BSMAINAMT/PLSUBAMT/BSSUBAMT
Company detection: TDL MyField approach
"""
import requests
import re
from datetime import datetime
from core.config import TALLY_URL, TALLY_TIMEOUT

def get_url(url: str | None = None) -> str:
    return url.strip() if url and url.strip() else TALLY_URL

def test_connection(tally_url: str | None = None) -> dict:
    try:
        url = get_url(tally_url)
        r = requests.post(url,
            data='<ENVELOPE><HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER></ENVELOPE>',
            headers={'Content-Type': 'application/xml'}, timeout=10)
        if r.status_code == 200 and 'RESPONSE' in r.text:
            return {'status': 'ok', 'message': 'Tally connected successfully'}
        return {'status': 'error', 'message': f'Unexpected response'}
    except Exception as e:
        return {'status': 'error',
                'message': 'Cannot connect to Tally. Ensure Tally is open on port 9000'}

def get_current_company(tally_url: str | None = None) -> str:
    """Get name of currently open company via TDL"""
    xml = """<ENVELOPE>
<HEADER><VERSION>1</VERSION><TALLYREQUEST>Export</TALLYREQUEST>
<TYPE>Data</TYPE><ID>MyReport</ID></HEADER>
<BODY><DESC><TDL><TDLMESSAGE>
<REPORT NAME="MyReport"><FORMS>MyForm</FORMS></REPORT>
<FORM NAME="MyForm"><PARTS>MyPart</PARTS></FORM>
<PART NAME="MyPart"><LINES>MyLine</LINES>
<REPEAT>MyLine : MyCollection</REPEAT>
<SCROLLED>Vertical</SCROLLED></PART>
<LINE NAME="MyLine"><FIELDS>MyField</FIELDS></LINE>
<FIELD NAME="MyField"><SET>$Name</SET></FIELD>
<COLLECTION NAME="MyCollection" ISINITIALIZE="Yes">
<TYPE>Company</TYPE>
</COLLECTION>
</TDLMESSAGE></TDL></DESC></BODY></ENVELOPE>"""
    try:
        url = get_url(tally_url)
        r = requests.post(url, data=xml.encode('utf-8'),
                         headers={'Content-Type': 'application/xml'}, timeout=TALLY_TIMEOUT)
        # Extract all company names
        names = re.findall(r'<MYFIELD>(.*?)</MYFIELD>', r.text)
        return [n.strip() for n in names if n.strip()]
    except Exception as e:
        print(f"[Tally] get_current_company error: {e}")
        return []

def get_all_companies(tally_url: str | None = None) -> list:
    """
    Returns list of all companies from Tally.
    Uses TDL approach which works with Tally Prime.
    """
    names = get_current_company(tally_url)
    return [{'name': n, 'books_from': ''} for n in names]

def fetch_pl_data(company: str, from_date: str, to_date: str, tally_url: str | None = None) -> str:
    """Fetch P&L data for a company and date range"""
    xml = f"""<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>Profit and Loss</REPORTNAME>
<STATICVARIABLES>
<SVFROMDATE>{from_date}</SVFROMDATE>
<SVTODATE>{to_date}</SVTODATE>
<SVCURRENTCOMPANY>{company}</SVCURRENTCOMPANY>
<EXPLODEFLAG>Yes</EXPLODEFLAG>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY></ENVELOPE>"""
    url = get_url(tally_url)
    r = requests.post(url, data=xml.encode('utf-8'),
                     headers={'Content-Type': 'application/xml'}, timeout=60)
    return r.text

def fetch_bs_data(company: str, from_date: str, to_date: str, tally_url: str | None = None) -> str:
    """Fetch Balance Sheet data"""
    xml = f"""<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>Balance Sheet</REPORTNAME>
<STATICVARIABLES>
<SVFROMDATE>{from_date}</SVFROMDATE>
<SVTODATE>{to_date}</SVTODATE>
<SVCURRENTCOMPANY>{company}</SVCURRENTCOMPANY>
<EXPLODEFLAG>Yes</EXPLODEFLAG>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY></ENVELOPE>"""
    url = get_url(tally_url)
    r = requests.post(url, data=xml.encode('utf-8'),
                     headers={'Content-Type': 'application/xml'}, timeout=60)
    return r.text

def tally_date(dt: datetime) -> str:
    return dt.strftime('%Y%m%d')

def from_tally_date(s: str):
    try:
        return datetime.strptime(s.strip()[:8], '%Y%m%d')
    except:
        return None
