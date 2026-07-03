"""Run: python fix_intellichemie.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== DIAGNOSIS ===\n")

# Check: how many companies have ledger_name='Indirect Expenses'
rows = conn.execute("""
    SELECT company_id, COUNT(*) as cnt, SUM(net) as total
    FROM pl_data WHERE ledger_name='Indirect Expenses'
    GROUP BY company_id
""").fetchall()
for r in rows:
    co = conn.execute("SELECT tally_name FROM companies WHERE id=?", (r['company_id'],)).fetchone()
    print(f"  company_id={r['company_id']} ({co['tally_name'] if co else 'unknown'}) → {r['cnt']} rows, {r['total']/1e5:.2f}L")

# Check months for Intellichemie
months = conn.execute("""
    SELECT DISTINCT year, month FROM pl_data WHERE company_id=1
    ORDER BY year, month
""").fetchall()
print(f"\nIntellichemie months in DB: {len(months)}")
for m in months[:5]:
    print(f"  {m['year']}-{m['month']:02d}")
if len(months) > 5:
    print(f"  ... and {len(months)-5} more")

# Tally: Intellichemie FY25-26 = Apr-25 to Mar-26
# Check if data exists
fy_rows = conn.execute("""
    SELECT COUNT(*), SUM(net) FROM pl_data WHERE company_id=1
    AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()
print(f"\nIntellichemie FY25-26 rows: {fy_rows[0]}, total: {(fy_rows[1] or 0)/1e5:.2f}L")

# Check: Direct Expenses per month for Intellichemie
print("\nDirect Expenses per month (Intellichemie FY25-26):")
de_months = conn.execute("""
    SELECT year, month, SUM(net) as total FROM pl_data
    WHERE company_id=1
      AND LOWER(tally_group)='direct expenses'
      AND ledger_name != 'Direct Expenses'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY year, month ORDER BY year, month
""").fetchall()
de_total = 0
for r in de_months:
    print(f"  {r['year']}-{r['month']:02d}: {r['total']/1e5:.2f}L")
    de_total += r['total']
print(f"  Total: {de_total/1e5:.2f}L  (Tally: -41.43L)")

# Check: why 59.17L vs Tally 41.43L
# 59.17 - 41.43 = 17.74L extra
# Intellichemie has some Direct Expenses rows with mis_group='Direct Expenses'
# but also _GROUP_TOTAL_ tagged rows not being skipped
print("\nDirect Expenses breakdown:")
de_detail = conn.execute("""
    SELECT mis_group, SUM(net) as total, COUNT(*) as cnt
    FROM pl_data WHERE company_id=1
      AND LOWER(tally_group)='direct expenses'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY mis_group
""").fetchall()
for r in de_detail:
    print(f"  mis='{r['mis_group']}' total={r['total']/1e5:.2f}L cnt={r['cnt']}")

# Check Cost of Sales
cos = conn.execute("""
    SELECT SUM(net) as total FROM pl_data
    WHERE company_id=1
      AND LOWER(tally_group)='cost of sales :'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()
print(f"\nCost of Sales (FY25-26): {(cos['total'] or 0)/1e5:.2f}L")

conn.close()
