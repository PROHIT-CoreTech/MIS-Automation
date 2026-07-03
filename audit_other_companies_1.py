"""Run: python audit_other_companies.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

companies = [
    (1, "Intellichemie Industries LLP"),
    (3, "Avenuecorp India Private Limited FY 23-24"),
]

for cid, name in companies:
    print(f"\n{'='*65}")
    print(f"COMPANY: {name}")
    print(f"{'='*65}")

    # All tally_groups in DB
    rows = conn.execute("""
        SELECT tally_group, mis_group,
               SUM(net) as total, COUNT(DISTINCT ledger_name) as ledgers
        FROM pl_data WHERE company_id=?
        GROUP BY tally_group, mis_group
        ORDER BY ABS(SUM(net)) DESC
    """, (cid,)).fetchall()

    print(f"\n  tally_group                    mis_group                        Total Cr  Ledgers")
    print("  " + "-"*85)
    for r in rows:
        tg = str(r['tally_group'] or '')
        mg = str(r['mis_group'] or '')
        v  = r['total'] or 0
        print(f"  {tg:30s} {mg:30s} {v/1e7:>8.2f}   {r['ledgers']}")

    # Check Sales Accounts group total
    sa = conn.execute("""
        SELECT SUM(net) as t FROM pl_data
        WHERE company_id=? AND tally_group='Sales Accounts'
        AND ledger_name='Sales Accounts'
    """, (cid,)).fetchone()
    print(f"\n  Sales Accounts group total = {(sa['t'] or 0)/1e7:.2f} Cr")

    # Check Cost of Sales
    cos = conn.execute("""
        SELECT SUM(net) as t FROM pl_data
        WHERE company_id=? AND LOWER(tally_group)='cost of sales :'
        AND LOWER(ledger_name)='cost of sales :'
    """, (cid,)).fetchone()
    print(f"  Cost of Sales net          = {(cos['t'] or 0)/1e7:.2f} Cr")

    # Check Indirect Expenses group total
    ie = conn.execute("""
        SELECT SUM(net) as t FROM pl_data
        WHERE company_id=? AND LOWER(tally_group)='indirect expenses'
        AND LOWER(ledger_name)='indirect expenses'
    """, (cid,)).fetchone()
    print(f"  Indirect Expenses total    = {(ie['t'] or 0)/1e7:.2f} Cr")

conn.close()
