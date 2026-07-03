"""Run: python verify_intellichemie_calc.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

# Exact _calc simulation for Intellichemie FY25-26
rows = conn.execute("""
    SELECT ledger_name, mis_group, tally_group, net
    FROM pl_data WHERE company_id=1
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchall()

rev=dir_g=dir_i=cos=oh_grp=oh_items=ind_inc=0
cos_found=oh_found=False

for r in rows:
    tg=str(r['tally_group'] or '').lower().strip()
    mg=str(r['mis_group']   or '').lower().strip()
    ln=str(r['ledger_name'] or '').lower().strip()
    v =abs(r['net'] or 0)

    if tg in HEADERS or mg in HEADERS: continue

    # Capture overhead group total FIRST
    if tg == 'indirect expenses' and ln == 'indirect expenses':
        oh_grp += v; oh_found=True; continue

    if mg == '_group_total_': continue
    if ln == tg and tg not in ('sales accounts','cost of sales :','direct incomes'):
        continue

    if tg == 'sales accounts':
        if mg == 'sales accounts': rev += v
    elif tg == 'direct incomes':
        if mg == 'direct incomes': dir_g += v
        else: dir_i += v
    elif tg == 'cost of sales :':
        cos += v; cos_found=True
    elif tg == 'indirect incomes':
        ind_inc += v
    elif tg in ('indirect expenses','salaries and bonus','salary accounts'):
        oh_items += v

dir_inc  = dir_g if dir_g else dir_i
overhead = oh_grp if oh_found else oh_items
cogs     = cos if cos_found else 0
gp       = rev + dir_inc - cogs
np_      = gp + ind_inc - overhead

TALLY = {
    'Revenue':   0,
    'COGS':      41_43_121.82,
    'GP':       -41_43_121.82,
    'Overhead':  2_23_03_136.54,
    'Ind Inc':   3_48_707.89,
    'NP':       -2_60_97_550.47,
}

print("INTELLICHEMIE FY25-26 — _calc simulation")
print(f"\n  {'':15s} {'PORTAL':>15s}  {'TALLY':>15s}  {'DIFF':>12s}  STATUS")
print("  " + "-"*65)
for name, portal, tally in [
    ('Revenue',   rev,      TALLY['Revenue']),
    ('COGS',      cogs,     TALLY['COGS']),
    ('GP',        gp,       TALLY['GP']),
    ('Ind Inc',   ind_inc,  TALLY['Ind Inc']),
    ('Overhead',  overhead, TALLY['Overhead']),
    ('NP',        np_,      TALLY['NP']),
]:
    diff = portal - tally
    ok = '✅' if abs(diff) < 10000 else ('🟡' if abs(diff) < 500000 else '❌')
    print(f"  {name:15s} {portal:>15,.2f}  {tally:>15,.2f}  {diff:>+12,.2f}  {ok}")

print(f"\n  cos_found = {cos_found}, oh_found = {oh_found}")
print(f"  cos value = {cos:>15,.2f}")
print(f"  oh_grp    = {oh_grp:>15,.2f}  ← Indirect Expenses group total")
print(f"  oh_items  = {oh_items:>15,.2f}  ← Individual sum")
print(f"  rev       = {rev:>15,.2f}")

# Also show what Revenue should be
print(f"\nNote: Tally shows 0 sales but DB has {rev/1e5:.2f}L in Sales Accounts")
print(f"This means Sales ledgers have transactions but Tally shows 0 NET")
print(f"Possible: Sales are offset by returns/debit notes in Tally")
conn.close()
