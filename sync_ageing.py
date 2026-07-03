"""
Run: python sync_ageing.py
Syncs Bills Receivable (Customer) and Bills Payable (Vendor) from Tally
Uses SVCURRENTCOMPANY to fetch company-specific data
"""
import requests, sqlite3, re, os
from datetime import datetime

TALLY_URL = "http://localhost:9000"
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')

def parse_tally_date(d):
    if not d: return None
    for fmt in ('%d-%b-%y', '%d-%b-%Y', '%d-%m-%Y'):
        try: return datetime.strptime(d.strip(), fmt).strftime('%Y-%m-%d')
        except: continue
    return None

def fetch_ageing(report_name, company_name):
    xml_req = f"""<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>{report_name}</REPORTNAME>
<STATICVARIABLES>
<SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
<SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY></ENVELOPE>"""
    resp = requests.post(TALLY_URL, data=xml_req.encode('utf-8'), timeout=30)
    return resp.text

def parse_bills(xml_text):
    bills = []
    blocks = xml_text.split('<BILLFIXED>')
    for block in blocks[1:]:
        try:
            date    = re.search(r'<BILLDATE>(.*?)</BILLDATE>', block)
            ref     = re.search(r'<BILLREF>(.*?)</BILLREF>', block)
            party   = re.search(r'<BILLPARTY>(.*?)</BILLPARTY>', block)
            after   = block.split('</BILLFIXED>')[-1] if '</BILLFIXED>' in block else block
            amt     = re.search(r'<BILLCL>(.*?)</BILLCL>', after)
            due     = re.search(r'<BILLDUE>(.*?)</BILLDUE>', after)
            overdue = re.search(r'<BILLOVERDUE>(.*?)</BILLOVERDUE>', after)

            if not (date and party and amt): continue
            amount = float(amt.group(1).strip()) if amt else 0
            if abs(amount) < 1: continue

            bills.append({
                'party_name':  party.group(1).strip() if party else '',
                'bill_ref':    ref.group(1).strip() if ref else '',
                'bill_date':   parse_tally_date(date.group(1).strip()) if date else None,
                'due_date':    parse_tally_date(due.group(1).strip()) if due else None,
                'amount':      abs(amount),
                'days_overdue': int(overdue.group(1).strip()) if overdue else 0,
            })
        except: continue
    return bills

def sync_company(conn, company_id, company_name):
    synced_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    results = {}

    for party_type, report_name in [
        ('customer', 'Bills Receivable'),
        ('vendor',   'Bills Payable'),
    ]:
        print(f"  Fetching {report_name} for '{company_name}'...", end=' ', flush=True)
        try:
            xml = fetch_ageing(report_name, company_name)
            if 'LINEERROR' in xml:
                print(f"❌ {xml[:80]}")
                results[party_type] = 0
                continue

            bills = parse_bills(xml)
            print(f"{len(bills)} bills")

            # Clear + insert
            conn.execute("DELETE FROM ageing_data WHERE company_id=? AND party_type=?",
                        (company_id, party_type))
            for b in bills:
                conn.execute("""
                    INSERT INTO ageing_data
                    (company_id, party_type, party_name, bill_ref, bill_date,
                     due_date, amount, days_overdue, synced_at)
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, (company_id, party_type, b['party_name'], b['bill_ref'],
                      b['bill_date'], b['due_date'], b['amount'],
                      b['days_overdue'], synced_at))
            results[party_type] = len(bills)

        except Exception as e:
            print(f"❌ Exception: {e}")
            results[party_type] = 0

    conn.commit()
    return results.get('customer',0), results.get('vendor',0)

# ── MAIN ─────────────────────────────────────────────────
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

companies = conn.execute(
    "SELECT id, tally_name FROM companies WHERE is_active=1"
).fetchall()

print(f"Syncing ageing for {len(companies)} companies...\n")
for co in companies:
    print(f"Company: {co['tally_name']}")
    tc, tv = sync_company(conn, co['id'], co['tally_name'])
    print(f"  ✅ Customers: {tc} bills, Vendors: {tv} bills\n")

print("=== FINAL SUMMARY ===")
for cid, cname in [(co['id'], co['tally_name']) for co in companies]:
    for pt in ['customer','vendor']:
        row = conn.execute("""
            SELECT COUNT(*) as bills, COUNT(DISTINCT party_name) as parties,
                   SUM(amount) as total
            FROM ageing_data WHERE company_id=? AND party_type=?
        """, (cid, pt)).fetchone()
        print(f"  {cname[:25]:25s} | {pt:8s} | {row['bills']:4d} bills | "
              f"{row['parties']:3d} parties | ₹{(row['total'] or 0)/1e7:.2f} Cr")

conn.close()
print("\nDone!")
