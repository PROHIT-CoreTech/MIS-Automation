"""Run: python audit_intellichemie.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("="*70)
print("INTELLICHEMIE — DB vs TALLY COMPARISON")
print("="*70)

TALLY = {
    'revenue':   0,           # Sales = 0 (no actual sales this period)
    'cogs':      41_43_121.82, # Direct Expenses only (no purchases)
    'gp':       -41_43_121.82, # Gross Loss
    'overhead': 2_23_03_136.54,
    'ind_inc':   3_48_707.89,
    'np':       -2_60_97_550.47, # Net Loss
}

# All pl_data for Intellichemie
rows = conn.execute("""
    SELECT tally_group, mis_group, ledger_name, SUM(net) as total
    FROM pl_data WHERE company_id=1
    GROUP BY tally_group, mis_group, ledger_name
    ORDER BY tally_group, ABS(SUM(net)) DESC
""").fetchall()

print("\n=== ALL LEDGERS IN DB ===")
print(f"{'TG':30s} {'MIS':30s} {'Ledger':35s} {'Val':>10s}")
print("-"*110)
for r in rows:
    print(f"  {str(r['tally_group'] or ''):28s} {str(r['mis_group'] or ''):28s} {str(r['ledger_name'] or ''):33s} {r['total']/1e5:>8.2f}L")

# Key checks
print("\n=== KEY CHECKS ===")

# 1. Direct Expenses (should be 41,43,121)
de = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data WHERE company_id=1
    AND LOWER(tally_group)='direct expenses'
    AND ledger_name != 'Direct Expenses'
""").fetchone()[0] or 0
print(f"\n1. Direct Expenses sum = {de:>15,.2f}  Tally = {41_43_121.82:>15,.2f}  Diff = {de-41_43_121.82:>+10.2f}")

# 2. Indirect Expenses (should be 2,23,03,136)
ie_grp = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data WHERE company_id=1
    AND LOWER(tally_group)='indirect expenses'
    AND LOWER(ledger_name)='indirect expenses'
""").fetchone()[0] or 0
ie_ind = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data WHERE company_id=1
    AND LOWER(tally_group)='indirect expenses'
    AND LOWER(ledger_name) != 'indirect expenses'
    AND mis_group != '_GROUP_TOTAL_'
""").fetchone()[0] or 0
print(f"\n2. Indirect Exp group total = {ie_grp:>12,.2f}  Tally = {2_23_03_136.54:>12,.2f}")
print(f"   Indirect Exp individual   = {ie_ind:>12,.2f}")

# 3. Indirect Incomes (should be 3,48,707)
ii = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data WHERE company_id=1
    AND LOWER(tally_group)='indirect incomes'
    AND mis_group != '_GROUP_TOTAL_'
""").fetchone()[0] or 0
print(f"\n3. Indirect Incomes = {ii:>12,.2f}  Tally = {3_48_707.89:>12,.2f}")

# 4. Sales
sa = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data WHERE company_id=1
    AND LOWER(tally_group)='sales accounts'
    AND LOWER(ledger_name)='sales accounts'
""").fetchone()[0] or 0
print(f"\n4. Sales group total = {sa:>12,.2f}  Tally = 0 (no sales)")

# Simulate _calc
rev    = sa  # group total
dir_g  = conn.execute("""SELECT SUM(ABS(net)) FROM pl_data WHERE company_id=1
    AND LOWER(tally_group)='direct incomes' AND LOWER(ledger_name)='direct incomes'
""").fetchone()[0] or 0
cos    = conn.execute("""SELECT SUM(ABS(net)) FROM pl_data WHERE company_id=1
    AND LOWER(tally_group)='cost of sales :' AND LOWER(ledger_name)='cost of sales :'
""").fetchone()[0] or 0
oh     = ie_grp  # use group total
gp     = rev + dir_g - de - cos  # Mode B: no cos_net, use direct expenses
np_    = gp + ii - oh

print(f"\n=== PORTAL CALCULATION ===")
print(f"  Revenue   = {rev:>12,.2f}  Tally = 0")
print(f"  Dir Inc   = {dir_g:>12,.2f}")
print(f"  Dir Exp   = {de:>12,.2f}  Tally = {41_43_121.82:>12,.2f}")
print(f"  GP        = {gp:>12,.2f}  Tally = {-41_43_121.82:>12,.2f}")
print(f"  Ind Inc   = {ii:>12,.2f}  Tally = {3_48_707.89:>12,.2f}")
print(f"  Overhead  = {oh:>12,.2f}  Tally = {2_23_03_136.54:>12,.2f}")
print(f"  NP        = {np_:>12,.2f}  Tally = {-2_60_97_550.47:>12,.2f}")

conn.close()
