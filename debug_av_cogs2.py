"""Run: python debug_av_cogs2.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== ALL rows with tg='cost of sales :' for Avenuecorp FY25-26 ===\n")
rows = conn.execute("""
    SELECT ledger_name, tally_group, mis_group,
           year, month, net
    FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='cost of sales :'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    ORDER BY year, month, ledger_name
""").fetchall()

total = 0
seen = {}
for r in rows:
    key = f"{r['ledger_name']}|{r['mis_group']}"
    seen[key] = seen.get(key,0) + (r['net'] or 0)

print(f"Total rows: {len(rows)}")
print(f"\nGrouped by ledger+mis:")
for k,v in sorted(seen.items(), key=lambda x: -abs(x[1])):
    ln, mg = k.split('|')
    print(f"  '{ln}' mis='{mg}' = {v/1e7:.4f} Cr")

total = sum(seen.values())
print(f"\nTotal: {abs(total)/1e7:.4f} Cr")
print(f"Expected: 15.83 Cr")

# Count rows per month
month_counts = conn.execute("""
    SELECT year, month, COUNT(*) as cnt, SUM(net) as total
    FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='cost of sales :'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY year, month ORDER BY year, month
""").fetchall()
print(f"\nRows per month:")
for r in month_counts:
    print(f"  {r['year']}-{r['month']:02d}: {r['cnt']} rows  {r['total']/1e7:.4f} Cr")

conn.close()
