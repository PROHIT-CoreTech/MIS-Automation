"""
Run this script on YOUR laptop to check what's in the portal DB.
Copy this file to: D:\Freelancing\MIS Portal\MIS_Portal\check_db.py
Then run: python check_db.py
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# 1. What companies are in DB?
print("=== COMPANIES IN DB ===")
cos = conn.execute("SELECT id, tally_name, sync_status, last_sync FROM companies").fetchall()
for c in cos:
    print(f"  ID={c['id']} | {c['tally_name']} | {c['sync_status']} | {c['last_sync']}")

# 2. For each company, show P&L summary
for co in cos:
    cid  = co['id']
    name = co['tally_name']
    print(f"\n=== P&L DATA: {name} ===")

    # All distinct MIS groups with totals
    rows = conn.execute("""
        SELECT mis_group, tally_group,
               SUM(net) as total_net,
               SUM(abs(net)) as total_abs,
               COUNT(*) as months
        FROM pl_data
        WHERE company_id=?
        GROUP BY mis_group, tally_group
        ORDER BY tally_group, mis_group
    """, (cid,)).fetchall()

    print(f"{'MIS Group':35s} {'Tally Group':30s} {'Net Total':>15s} {'Abs Total':>15s} {'Months':>6s}")
    print("-"*105)
    for r in rows:
        print(f"  {str(r['mis_group'] or ''):33s} {str(r['tally_group'] or ''):28s} "
              f"{r['total_net']:>15,.0f} {r['total_abs']:>15,.0f} {r['months']:>6d}")

    # Grand totals
    total = conn.execute(
        "SELECT SUM(net) as t, SUM(abs(net)) as a FROM pl_data WHERE company_id=?", (cid,)
    ).fetchone()
    print(f"\n  GRAND TOTAL NET: {total['t']:,.0f}  |  ABS: {total['a']:,.0f}")

    # Check Apr-25 to Mar-26 specifically
    print(f"\n  Apr-25 to Mar-26 (year=2025 month>=4 OR year=2026 month<=3):")
    fy = conn.execute("""
        SELECT mis_group, tally_group, SUM(net) as total
        FROM pl_data
        WHERE company_id=?
          AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
        GROUP BY mis_group, tally_group
        ORDER BY tally_group
    """, (cid,)).fetchall()
    for r in fy:
        if r['total'] and abs(r['total']) > 100000:
            print(f"    {str(r['mis_group'] or ''):35s} {str(r['tally_group'] or ''):28s} {r['total']:>15,.0f}")

conn.close()
print("\nDone!")
