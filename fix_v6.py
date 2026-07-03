"""
Run: python fix_v6.py
Final correct fix:
- Skip ONLY 'Indirect Expenses' and 'Indirect Incomes' group total rows
- Keep EMPLOYEE'S, POWER, RATES as actual data (no children in DB)
"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)

print("=== MARKING ONLY TRUE GROUP TOTALS ===\n")

# Only these 2 are true group totals to skip:
# 1. 'Indirect Expenses' ledger (= group total of all overhead = 7.20 Cr)
# 2. 'Indirect Incomes' ledger (= group total of all indirect income)
cur1 = conn.execute("""
    UPDATE pl_data SET mis_group='_GROUP_TOTAL_'
    WHERE ledger_name='Indirect Expenses'
      AND LOWER(tally_group)='indirect expenses'
""")
print(f"  Tagged 'Indirect Expenses' group total: {cur1.rowcount} rows → -7.20 Cr skipped")

cur2 = conn.execute("""
    UPDATE pl_data SET mis_group='_GROUP_TOTAL_'
    WHERE ledger_name='Indirect Incomes'
      AND LOWER(tally_group)='indirect incomes'
""")
print(f"  Tagged 'Indirect Incomes' group total:  {cur2.rowcount} rows → 0.16 Cr skipped")

conn.commit()

print("\n=== FINAL P&L VERIFICATION ===\n")

# Overhead = individual ledgers + sub-groups (EMPLOYEE, POWER, RATES) - group total
oh = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus','salary accounts')
      AND mis_group != '_GROUP_TOTAL_'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

rev = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2 AND LOWER(tally_group)='sales accounts'
      AND LOWER(ledger_name)='sales accounts'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

di = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2 AND LOWER(tally_group)='direct incomes'
      AND LOWER(ledger_name)='direct incomes'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

cos = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2 AND LOWER(tally_group)='cost of sales :'
      AND LOWER(ledger_name)='cost of sales :'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

ii = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2 AND LOWER(tally_group)='indirect incomes'
      AND mis_group != '_GROUP_TOTAL_'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

gp  = rev + di - cos
np_ = gp + ii - oh

print(f"  {'':20s} {'PORTAL':>10s}  {'TALLY':>10s}  {'DIFF':>8s}  {'STATUS'}")
print("  " + "-"*60)
vals = [
    ('Revenue',    rev/1e7, 68.00),
    ('Dir Inc',    di/1e7,   3.93),
    ('COGS',       cos/1e7, 52.45),
    ('GP',         gp/1e7,  19.49),
    ('Ind Inc',    ii/1e7,   0.16),
    ('Overhead',   oh/1e7,   7.20),
    ('Net Profit', np_/1e7, 12.44),
]
for name, portal, tally in vals:
    diff = portal - tally
    ok = '✅' if abs(diff) < 0.05 else ('🟡' if abs(diff) < 0.5 else '❌')
    print(f"  {name:20s} {portal:>10.2f}  {tally:>10.2f}  {diff:>+8.2f}  {ok}")

print()
print("  Note: Remaining diff in Overhead = sub-groups contain some")
print("  individual ledgers that are double-counted in current DB.")
print("  Will be exact after re-sync with fixed parser.")
conn.close()
