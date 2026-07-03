"""
Run: python fix_group_total.py
Marks group total rows with a special mis_group so they can be skipped
"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)

# Find all rows where ledger_name == tally_group (group total rows)
rows = conn.execute("""
    SELECT ledger_name, tally_group, mis_group, COUNT(*) as cnt, SUM(net) as total
    FROM pl_data
    WHERE company_id=2
      AND LOWER(ledger_name) = LOWER(tally_group)
    GROUP BY ledger_name, tally_group, mis_group
    ORDER BY ABS(SUM(net)) DESC
""").fetchall()

print("GROUP TOTAL ROWS (ledger_name == tally_group):")
print(f"{'Ledger':35s} {'MIS Group':30s} {'Total':>12s}")
print("-"*80)
for r in rows:
    print(f"  {str(r[0]):33s} {str(r[2]):30s} {r[4]/1e7:>10.2f} Cr  ({r[3]} rows)")

# Tag all group total rows with '_GROUP_TOTAL_' so _is_skip catches them
cur = conn.execute("""
    UPDATE pl_data
    SET mis_group = '_GROUP_TOTAL_'
    WHERE LOWER(ledger_name) = LOWER(tally_group)
      AND LOWER(tally_group) NOT IN (
          'sales accounts',
          'direct incomes',
          'cost of sales :'
      )
""")
conn.commit()
print(f"\n✅ Tagged {cur.rowcount} group total rows as '_GROUP_TOTAL_'")
print("  (Sales Accounts, Direct Incomes, Cost of Sales : kept for calculation)")

# Verify overhead now
rows2 = conn.execute("""
    SELECT SUM(ABS(net)) as total
    FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus')
      AND mis_group != '_GROUP_TOTAL_'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()
print(f"\nOverhead after fix: {rows2[0]/1e7:.2f} Cr  (expected 7.20 Cr)")
conn.close()
