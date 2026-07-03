"""
Run: python fix_db3.py
Fixes double counting by identifying and removing group total rows
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# The problem: ledger_name='Indirect Expenses' stored in pl_data
# This IS the group total row — same name as tally_group
# Also: 'EMPLOYEE'S RELATED EXPENSES' is a sub-group total

print("=== CHECKING LEDGER NAMES THAT MATCH TALLY GROUP NAMES ===")
# These are group total rows — ledger_name == tally_group (or sub-group name)
problem_rows = conn.execute("""
    SELECT ledger_name, tally_group, mis_group,
           COUNT(*) as rows,
           SUM(net) as total
    FROM pl_data
    WHERE company_id=2
      AND LOWER(ledger_name) = LOWER(tally_group)
    GROUP BY ledger_name, tally_group, mis_group
    ORDER BY ABS(SUM(net)) DESC
""").fetchall()

print(f"\n{'Ledger Name':45s} {'Tally Group':25s} {'Total':>15s} {'Rows':>6s}")
print("-"*95)
for r in problem_rows:
    print(f"  {str(r['ledger_name']):43s} {str(r['tally_group']):25s} {abs(r['total'] or 0):>15,.2f} {r['rows']:>6d}")

print(f"\nThese are group total rows — ledger_name == tally_group")
print(f"They should be SKIPPED in calculation")

# Verify: if we exclude 'Indirect Expenses' ledger row from overhead:
print("\n=== WHAT OVERHEAD WOULD BE WITHOUT GROUP TOTAL ROWS ===")
correct_oh = conn.execute("""
    SELECT SUM(net) as total
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus','salary accounts')
      AND LOWER(ledger_name) != LOWER(tally_group)
""").fetchone()

print(f"  Overhead (excl group total rows) = {abs(correct_oh['total'] or 0):>15,.2f} = {abs(correct_oh['total'] or 0)/1e7:.2f} Cr")
print(f"  Tally Overhead                   =   72,009,881.92 =  7.20 Cr")
print(f"  Diff = {abs(correct_oh['total'] or 0) - 72009881.92:>+,.2f}")

# Full P&L with this fix
print("\n=== FULL P&L WITH FIX ===")
rows = conn.execute("""
    SELECT tally_group, mis_group, ledger_name, SUM(net) as s
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY tally_group, mis_group, ledger_name
""").fetchall()

rev = dir_g = dir_i = cos = oh = ind_inc = 0
for r in rows:
    tg  = str(r['tally_group']  or '').lower().strip()
    mg  = str(r['mis_group']    or '').lower().strip()
    ln  = str(r['ledger_name']  or '').lower().strip()
    v   = abs(r['s'] or 0)

    # Skip if ledger_name == tally_group (group total)
    if ln == tg: continue

    if   tg == 'sales accounts' and mg == 'sales accounts': rev    += v
    elif tg == 'direct incomes' and mg == 'direct incomes': dir_g  += v
    elif tg == 'direct incomes':                            dir_i  += v
    elif tg == 'cost of sales :':                           cos    += v
    elif tg == 'indirect incomes':                          ind_inc+= v
    elif tg in ('indirect expenses','salaries and bonus','salary accounts'):
        oh += v

dir_inc = max(dir_g, dir_i)
gp  = rev + dir_inc - cos
np_ = gp + ind_inc - oh

print(f"\n  {'':20s} {'Portal':>12s}  {'Tally':>12s}  {'Diff':>10s}")
print("  " + "-"*55)
print(f"  {'Revenue':20s} {rev/1e7:>11.2f}  {68.00:>11.2f}  {rev/1e7-68.00:>+9.2f}")
print(f"  {'Gross Profit':20s} {gp/1e7:>11.2f}  {19.49:>11.2f}  {gp/1e7-19.49:>+9.2f}")
print(f"  {'Overhead':20s} {oh/1e7:>11.2f}  {7.20:>11.2f}  {oh/1e7-7.20:>+9.2f}")
print(f"  {'Net Profit':20s} {np_/1e7:>11.2f}  {12.44:>11.2f}  {np_/1e7-12.44:>+9.2f}")

conn.close()
