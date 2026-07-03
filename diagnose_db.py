"""
Run: python diagnose_db.py
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

cos = conn.execute("SELECT id, tally_name FROM companies").fetchall()

for co in cos:
    cid, name = co['id'], co['tally_name']
    print(f"\n{'='*70}")
    print(f"COMPANY: {name}  (id={cid})")
    print(f"{'='*70}")

    # Show ALL unique tally_group values + their totals
    rows = conn.execute("""
        SELECT
            tally_group,
            mis_group,
            SUM(net)                    as net_total,
            COUNT(DISTINCT ledger_name) as ledger_count
        FROM pl_data
        WHERE company_id=?
          AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
        GROUP BY tally_group, mis_group
        ORDER BY ABS(SUM(net)) DESC
    """, (cid,)).fetchall()

    print(f"\n  {'tally_group':35s} {'mis_group':30s} {'net_total':>15s} {'ledgers':>8s}")
    print("  " + "-"*92)
    for r in rows:
        print(f"  {str(r['tally_group'] or 'NULL'):35s} "
              f"{str(r['mis_group']   or 'NULL'):30s} "
              f"{r['net_total']:>15,.0f}  {r['ledger_count']:>7d}")

    # Key check: is 'Cost of Sales :' present?
    cos_row = conn.execute("""
        SELECT SUM(net) as total FROM pl_data
        WHERE company_id=?
          AND LOWER(tally_group) = 'cost of sales :'
          AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    """, (cid,)).fetchone()

    print(f"\n  KEY CHECK:")
    print(f"  'Cost of Sales :' total = {cos_row['total'] or 0:,.0f}")

    # Check what's in tally_group column raw
    sample = conn.execute("""
        SELECT DISTINCT tally_group FROM pl_data
        WHERE company_id=? AND tally_group IS NOT NULL
        ORDER BY tally_group
    """, (cid,)).fetchall()
    print(f"\n  ALL tally_group values in DB:")
    for r in sample:
        print(f"    '{r['tally_group']}'")

conn.close()
