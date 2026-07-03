"""Run: python verify_avenuecorp_full.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# TALLY VALUES (from screenshots)
TALLY = {
    'revenue':   27_90_82_711.93,
    'cogs':      15_81_44_357.93,  # Opening(3.97) + Purchase(13.47) + DirectExp(0.36) - Closing(1.96)
    'gp':        12_07_37_877.00,  # from Tally screenshot directly
    'overhead':   6_15_35_679.71,  # IE(2.41) + Salaries(3.74)
    'ind_inc':    0,               # need to check
    'np':         5_93_09_000.66,
}

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

# Avenuecorp = company_id=3, data period
avail = conn.execute("""
    SELECT MIN(year*100+month) as mn, MAX(year*100+month) as mx
    FROM pl_data WHERE company_id=3
""").fetchone()
mn, mx = avail['mn'], avail['mx']
fy, fm = mn//100, mn%100
ty, tm = mx//100, mx%100
print(f"Avenuecorp data period: {fm}/{fy} to {tm}/{ty}")

rows = conn.execute("""
    SELECT ledger_name, mis_group, tally_group, net
    FROM pl_data WHERE company_id=3
""").fetchall()
print(f"Total rows: {len(rows)}")

rev=dir_g=dir_i=cos=oh_grp=oh_items=ind_inc=0
cos_found=oh_found=False

for r in rows:
    tg=str(r['tally_group'] or '').lower().strip()
    mg=str(r['mis_group']   or '').lower().strip()
    ln=str(r['ledger_name'] or '').lower().strip()
    v =abs(r['net'] or 0)

    if tg in HEADERS or mg in HEADERS: continue

    # Capture overhead group total FIRST (before _GROUP_TOTAL_ skip)
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

print(f"\n{'':15s} {'PORTAL':>15s}  {'TALLY':>15s}  {'DIFF':>12s}  STATUS")
print("-"*65)
for name, portal, tally in [
    ('Revenue',  rev/1e7,     TALLY['revenue']/1e7),
    ('COGS',     cogs/1e7,    TALLY['cogs']/1e7),
    ('GP',       gp/1e7,      TALLY['gp']/1e7),
    ('Overhead', overhead/1e7,TALLY['overhead']/1e7),
    ('Ind Inc',  ind_inc/1e7, TALLY['ind_inc']/1e7),
    ('NP',       np_/1e7,     TALLY['np']/1e7),
]:
    diff=portal-tally
    ok='✅' if abs(diff)<0.05 else ('🟡' if abs(diff)<1.0 else '❌')
    print(f"  {name:15s} {portal:>13.4f}Cr  {tally:>13.4f}Cr  {diff:>+10.4f}  {ok}")

print(f"\noh_grp (IE group total)  = {oh_grp/1e7:.4f} Cr  (Tally IE = 2.41 Cr)")
print(f"oh_items (individual)    = {oh_items/1e7:.4f} Cr")
print(f"oh_found = {oh_found}")
print(f"\nSalaries in DB:")

sal = conn.execute("""
    SELECT mis_group, SUM(net) as total, COUNT(*) as cnt
    FROM pl_data WHERE company_id=3
    AND LOWER(tally_group)='salaries and bonus'
    GROUP BY mis_group
""").fetchall()
for r in sal:
    print(f"  mis='{r['mis_group']}' total={r['total']/1e7:.4f}Cr cnt={r['cnt']}")

print(f"\nNOTE: Tally Overhead = IE(2.41) + Salaries(3.74) = 6.15 Cr")
print(f"Portal uses ONLY 'Indirect Expenses' group total = {oh_grp/1e7:.2f} Cr")
print(f"Salaries and Bonus = SEPARATE group in Tally, not under Indirect Expenses")
print(f"Portal needs to add Salaries group total to overhead!")

conn.close()
