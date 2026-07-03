"""
Run: python check_pl2.py
Shows EXACT tally_group breakdown for current FY
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

cos = conn.execute("SELECT id, tally_name FROM companies").fetchall()

for co in cos:
    cid  = co['id']
    name = co['tally_name']
    print(f"\n{'='*75}")
    print(f"COMPANY: {name}")
    print(f"{'='*75}")

    rows = conn.execute("""
        SELECT tally_group, mis_group,
               SUM(net)          as net_sum,
               SUM(abs(net))     as abs_sum,
               COUNT(DISTINCT ledger_name) as ledgers
        FROM pl_data
        WHERE company_id=?
          AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
        GROUP BY tally_group, mis_group
        ORDER BY tally_group, abs(SUM(net)) DESC
    """, (cid,)).fetchall()

    if not rows:
        print("  No data for FY25-26")
        continue

    print(f"\n  {'Tally Group':35s} {'MIS Group':35s} {'Net Sum':>15s} {'Ledgers':>8s}")
    print("  " + "-"*97)
    for r in rows:
        print(f"  {str(r['tally_group'] or 'NULL'):35s} "
              f"{str(r['mis_group']   or 'NULL'):35s} "
              f"{r['net_sum']:>15,.0f} {r['ledgers']:>8d}")

conn.close()
