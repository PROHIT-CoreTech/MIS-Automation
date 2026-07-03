"""
Run this on your laptop:
cd D:\Freelancing\MIS Portal\MIS_Portal
python check_pl.py
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# Get all companies
cos = conn.execute("SELECT id, tally_name FROM companies").fetchall()

for co in cos:
    cid  = co['id']
    name = co['tally_name']
    print(f"\n{'='*70}")
    print(f"COMPANY: {name}")
    print(f"{'='*70}")

    # Show ALL distinct tally_group values with their net totals
    rows = conn.execute("""
        SELECT tally_group, mis_group,
               SUM(net) as net_total,
               SUM(abs(net)) as abs_total,
               COUNT(*) as cnt
        FROM pl_data
        WHERE company_id=?
          AND year=2025 AND month BETWEEN 4 AND 12
          OR (company_id=? AND year=2026 AND month BETWEEN 1 AND 3)
        GROUP BY tally_group, mis_group
        ORDER BY tally_group, abs_total DESC
    """, (cid, cid)).fetchall()

    print(f"\n{'Tally Group':30s} {'MIS Group':35s} {'Net Total':>15s} {'Count':>6s}")
    print("-"*90)
    for r in rows:
        print(f"  {str(r['tally_group'] or ''):28s} {str(r['mis_group'] or ''):33s} "
              f"{r['net_total']:>15,.0f} {r['cnt']:>6d}")

conn.close()
