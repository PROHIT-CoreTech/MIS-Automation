"""Run: python test_new_logic.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

rows = conn.execute("""
    SELECT ledger_name, mis_group, tally_group, year, month, net
    FROM pl_data WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchall()

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

rev_total=dir_inc_total=dir_inc_items=cos_net=ind_inc=oh_items=oh_grp=0
cos_net_found=oh_grp_found=False
b={'opening':0,'purchases':0,'direct_exp':0,'closing':0}

for r in rows:
    tg=str(r['tally_group'] or '').lower().strip()
    mg=str(r['mis_group']   or '').lower().strip()
    ln=str(r['ledger_name'] or '').lower().strip()
    val=abs(r['net'] or 0)

    # Capture BEFORE skip rules — same as how COGS captures 'cost of sales :'
    if tg == 'indirect expenses' and ln == 'indirect expenses':
        oh_grp += val; oh_grp_found=True; continue

    if tg in HEADERS or mg in HEADERS: continue
    if mg == '_group_total_': continue

    if ln == tg and tg not in ('sales accounts','cost of sales :','direct incomes'):
        continue

    if tg == 'sales accounts':
        if mg == 'sales accounts': rev_total += val
        continue
    if tg == 'direct incomes':
        if mg == 'direct incomes': dir_inc_total += val
        else: dir_inc_items += val
        continue
    if tg == 'cost of sales :':
        cos_net += val; cos_net_found=True; continue
    if tg == 'indirect incomes':
        ind_inc += val; continue
    if tg in ('indirect expenses','salaries and bonus','salary accounts'):
        oh_items += val; continue

dir_inc  = dir_inc_total if dir_inc_total else dir_inc_items
cogs     = cos_net if cos_net_found else 0
overhead = oh_grp if oh_grp_found else oh_items
gp       = rev_total + dir_inc - cogs
np_      = gp + ind_inc - overhead

print(f"{'':15s} {'PORTAL':>10s}  {'TALLY':>10s}  {'DIFF':>8s}  STATUS")
print("-"*55)
for name,portal,tally in [
    ('Revenue',  rev_total/1e7, 68.00),
    ('Dir Inc',  dir_inc/1e7,    3.93),
    ('COGS',     cogs/1e7,      52.45),
    ('GP',       gp/1e7,        19.49),
    ('Ind Inc',  ind_inc/1e7,    0.16),
    ('Overhead', overhead/1e7,   7.20),
    ('NP',       np_/1e7,       12.44),
]:
    diff=portal-tally
    ok='✅' if abs(diff)<0.02 else ('🟡' if abs(diff)<0.10 else '❌')
    print(f"{name:15s} {portal:>10.4f}  {tally:>10.4f}  {diff:>+8.4f}  {ok}")

print(f"\noh_grp_found = {oh_grp_found}")
print(f"oh_grp (Tally net)  = {oh_grp/1e7:.4f} Cr  ← Expected 7.20 Cr")
print(f"oh_items (sum)      = {oh_items/1e7:.4f} Cr  ← Was being used before")
conn.close()
