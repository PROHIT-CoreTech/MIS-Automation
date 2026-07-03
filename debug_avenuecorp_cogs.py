"""Run: python debug_avenuecorp_cogs.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== AVENUECORP COGS ANALYSIS ===\n")

# Cost of Sales per month FY25-26
print("Cost of Sales : per month (FY25-26):")
cos_months = conn.execute("""
    SELECT year, month, ledger_name, mis_group, SUM(net) as total, COUNT(*) as cnt
    FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='cost of sales :'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY year, month, ledger_name, mis_group
    ORDER BY year, month
""").fetchall()

cos_total = 0
for r in cos_months:
    print(f"  {r['year']}-{r['month']:02d}: ledger='{r['ledger_name']}' mis='{r['mis_group']}' val={r['total']/1e7:.4f}Cr cnt={r['cnt']}")
    cos_total += r['total']
print(f"  Total: {abs(cos_total)/1e7:.4f} Cr  Tally=15.8144 Cr")

# Check group total row
print("\nCost of Sales : group total:")
cos_grp = conn.execute("""
    SELECT year, month, SUM(net) as total
    FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='cost of sales :'
      AND LOWER(ledger_name)='cost of sales :'
    GROUP BY year, month ORDER BY year, month
""").fetchall()
for r in cos_grp:
    print(f"  {r['year']}-{r['month']:02d}: {r['total']/1e7:.4f}Cr")

# Why is COGS 19.87 vs 15.81?
# Diff = 4.05 Cr
# Check if any other tally_group contributes to COGS
print("\nAll tally_groups contributing to COGS in _calc:")
print("(tg='cost of sales :' + cos_net_found=True)")

# Tally COGS = Opening(3.97) + Purchase(13.47) + DirectExp(0.36) - Closing(1.96) = 15.81
# But Tally's 'Cost of Sales :' group total should = 15.81
# If portal shows 19.87, the group total row must have wrong value

# Check what value is in group total
cos_val = conn.execute("""
    SELECT SUM(net) as total FROM pl_data
    WHERE company_id=3
      AND LOWER(tally_group)='cost of sales :'
      AND LOWER(ledger_name)='cost of sales :'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()
print(f"\nCost of Sales group total (FY25-26) = {abs(cos_val['total'] or 0)/1e7:.4f} Cr")
print(f"Tally = 15.8144 Cr")
print(f"Diff  = {abs(cos_val['total'] or 0)/1e7 - 15.8144:.4f} Cr")

# Compare with Avenuecorp Tally values:
# Opening Stock = 3,96,60,400 = 3.97 Cr
# Purchases = 13,46,67,160 = 13.47 Cr
# Direct Exp = 36,20,674 = 0.36 Cr
# Closing Stock = 1,96,03,400 = 1.96 Cr
# COGS = 3.97 + 13.47 + 0.36 - 1.96 = 15.84 Cr (rounding)

conn.close()
