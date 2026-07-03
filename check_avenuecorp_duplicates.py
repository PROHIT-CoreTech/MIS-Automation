"""Run: python check_avenuecorp_duplicates.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== AVENUECORP FY25-26 DATA CHECK ===\n")

# Check row count per month
months = conn.execute("""
    SELECT year, month, COUNT(*) as cnt, SUM(net) as total
    FROM pl_data WHERE company_id=3
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY year, month ORDER BY year, month
""").fetchall()

print("Rows per month:")
total_rows = 0
for m in months:
    print(f"  {m['year']}-{m['month']:02d}: {m['cnt']:4d} rows  {m['total']/1e7:.2f}Cr")
    total_rows += m['cnt']
print(f"Total: {total_rows} rows")

# Check for duplicates - same ledger same month multiple times
dups = conn.execute("""
    SELECT ledger_name, tally_group, year, month, COUNT(*) as cnt, SUM(net) as total
    FROM pl_data WHERE company_id=3
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, tally_group, year, month
    HAVING COUNT(*) > 1
    ORDER BY COUNT(*) DESC
    LIMIT 10
""").fetchall()

print(f"\nDuplicate rows (same ledger+month): {len(dups)}")
for r in dups:
    print(f"  '{r['ledger_name']}' {r['year']}-{r['month']:02d} → {r['cnt']}x {r['total']/1e7:.4f}Cr")

# Check Sales Accounts specifically
sa = conn.execute("""
    SELECT ledger_name, year, month, COUNT(*) as cnt, SUM(net) as total
    FROM pl_data WHERE company_id=3
      AND tally_group='Sales Accounts'
      AND ledger_name='Sales Accounts'
    GROUP BY ledger_name, year, month
    ORDER BY year, month
""").fetchall()

print(f"\nSales Accounts group total rows per month:")
sa_annual = 0
for r in sa:
    print(f"  {r['year']}-{r['month']:02d}: {r['cnt']}x  {r['total']/1e7:.4f}Cr")
    if (r['year']==2025 and r['month']>=4) or (r['year']==2026 and r['month']<=3):
        sa_annual += r['total']
print(f"Annual total (FY25-26): {sa_annual/1e7:.4f}Cr  Tally=27.91Cr")

# Check if data exists for multiple FY periods
print(f"\nAll years in DB for Avenuecorp:")
yrs = conn.execute("""
    SELECT year, COUNT(*) as cnt, SUM(net) as total
    FROM pl_data WHERE company_id=3
    GROUP BY year ORDER BY year
""").fetchall()
for r in yrs:
    print(f"  {r['year']}: {r['cnt']} rows  {r['total']/1e7:.2f}Cr")

conn.close()
