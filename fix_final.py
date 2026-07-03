"""
Run: python fix_final.py
Precise fix — only tag actual sub-group totals in overhead
"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)

print("=== STEP 1: Restore Sales Accounts and Direct Incomes ===")

# Restore Sales Accounts individual ledgers (not the group total)
cur = conn.execute("""
    UPDATE pl_data SET mis_group='Domestic Sales'
    WHERE ledger_name IN ('GST SALES','IGST SALES','Sales Bills to Make')
      AND mis_group='_GROUP_TOTAL_'
""")
print(f"  Restored GST/IGST Sales: {cur.rowcount} rows")

cur = conn.execute("""
    UPDATE pl_data SET mis_group='EXPORT SALES'
    WHERE ledger_name='EXPORT SALES' AND mis_group='_GROUP_TOTAL_'
""")
print(f"  Restored EXPORT SALES: {cur.rowcount} rows")

cur = conn.execute("""
    UPDATE pl_data SET mis_group='Sales Accounts'
    WHERE ledger_name IN ('Goods Sold As Free of Cost')
      AND mis_group='_GROUP_TOTAL_'
""")
print(f"  Restored Goods Sold As Free: {cur.rowcount} rows")

# Restore Direct Incomes individual ledgers
cur = conn.execute("""
    UPDATE pl_data SET mis_group='Direct Incomes'
    WHERE ledger_name IN (
        'AMC Service Charges','Foundation Scheme Income','Installation Charges',
        'Job Work Charges Received','Packing Charges','Service Charges',
        'Turnover Discount','Freight Outword','Packing Charges'
    )
    AND mis_group='_GROUP_TOTAL_'
""")
print(f"  Restored Direct Incomes ledgers: {cur.rowcount} rows")

print("\n=== STEP 2: Keep only true sub-group totals tagged ===")
# These are the ONLY overhead sub-group totals to skip:
# EMPLOYEE'S RELATED EXPENSES — sub-group total (salary/ESIC/PF)
# POWER & FUEL EXPENSES — sub-group total
# RATES AND TAXES — sub-group total
# Indirect Expenses — main group total
# Indirect Incomes — main group total

# Check what's currently tagged
tagged = conn.execute("""
    SELECT ledger_name, tally_group, COUNT(*) as cnt, SUM(net) as total
    FROM pl_data
    WHERE mis_group='_GROUP_TOTAL_'
      AND company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, tally_group
    ORDER BY ABS(SUM(net)) DESC
""").fetchall()
print("\nCurrently _GROUP_TOTAL_ tagged (USP FY25-26):")
for r in tagged:
    print(f"  '{r[0]}' tg='{r[1]}' {r[3]/1e7:.3f} Cr ({r[2]} rows)")

conn.commit()

print("\n=== STEP 3: Verify P&L ===")
# Overhead
oh = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus','salary accounts')
      AND mis_group != '_GROUP_TOTAL_'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

# Revenue (using group total)
rev = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group)='sales accounts'
      AND LOWER(ledger_name)='sales accounts'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

# Direct Incomes group total
di = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group)='direct incomes'
      AND LOWER(ledger_name)='direct incomes'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

# Indirect Incomes
ii = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group)='indirect incomes'
      AND mis_group != '_GROUP_TOTAL_'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

# COGS
cos = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group)='cost of sales :'
      AND LOWER(ledger_name)='cost of sales :'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

gp = rev + di - cos
np_ = gp + ii - oh

print(f"\n  {'':20s} {'PORTAL':>10s}  {'TALLY':>10s}  {'DIFF':>8s}")
print("  " + "-"*52)
print(f"  {'Revenue':20s} {rev/1e7:>10.2f}  {68.00:>10.2f}  {rev/1e7-68.00:>+8.2f}")
print(f"  {'Dir Inc':20s} {di/1e7:>10.2f}  {3.93:>10.2f}  {di/1e7-3.93:>+8.2f}")
print(f"  {'COGS':20s} {cos/1e7:>10.2f}  {52.45:>10.2f}  {cos/1e7-52.45:>+8.2f}")
print(f"  {'GP':20s} {gp/1e7:>10.2f}  {19.49:>10.2f}  {gp/1e7-19.49:>+8.2f}")
print(f"  {'Ind Inc':20s} {ii/1e7:>10.2f}  {0.16:>10.2f}  {ii/1e7-0.16:>+8.2f}")
print(f"  {'Overhead':20s} {oh/1e7:>10.2f}  {7.20:>10.2f}  {oh/1e7-7.20:>+8.2f}")
print(f"  {'Net Profit':20s} {np_/1e7:>10.2f}  {12.44:>10.2f}  {np_/1e7-12.44:>+8.2f}")

conn.close()
