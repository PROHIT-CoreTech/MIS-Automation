"""Run: python debug_gp.py — Find why GP=23.43 instead of 19.49"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# Simulate exact _calc for USP Apr-25 to Mar-26
rows = conn.execute("""
    SELECT ledger_name, mis_group, tally_group, year, month, net
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    ORDER BY year, month
""").fetchall()

rev_total=0; dir_inc_total=0; dir_inc_items=0
cos_net=0; cos_net_found=False
ind_inc=0; overhead=0
b={'opening':0,'purchases':0,'direct_exp':0,'closing':0}

HEADERS={'trading account:','profit & loss a/c','gross profit :',
         'gross profit c/o','gross profit b/f','nett profit','net profit'}

for r in rows:
    tg  = str(r['tally_group'] or '').lower().strip()
    mg  = str(r['mis_group']   or '').lower().strip()
    ln  = str(r['ledger_name'] or '').lower().strip()
    val = abs(r['net'] or 0)

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
        cos_net += val; cos_net_found = True; continue
    if tg == 'indirect incomes':
        ind_inc += val; continue
    if tg in ('indirect expenses','salaries and bonus','salary accounts'):
        overhead += val; continue

dir_inc = dir_inc_total if dir_inc_total else dir_inc_items
cogs = cos_net if cos_net_found else (b['opening']+b['purchases']+b['direct_exp']-b['closing'])
gp   = rev_total + dir_inc - cogs
np_  = gp + ind_inc - overhead

print(f"rev_total     = {rev_total/1e7:.4f} Cr  ← should be 68.00")
print(f"dir_inc_total = {dir_inc_total/1e7:.4f} Cr  ← should be 3.94")
print(f"dir_inc_items = {dir_inc_items/1e7:.4f} Cr")
print(f"dir_inc used  = {dir_inc/1e7:.4f} Cr")
print(f"cos_net       = {cos_net/1e7:.4f} Cr  ← should be 52.45")
print(f"GP            = {gp/1e7:.4f} Cr  ← should be 19.49")
print(f"ind_inc       = {ind_inc/1e7:.4f} Cr  ← should be 0.16")
print(f"overhead      = {overhead/1e7:.4f} Cr  ← should be 7.20")
print(f"NP            = {np_/1e7:.4f} Cr  ← should be 12.44")

if abs(rev_total/1e7 - 68.00) > 0.1:
    print(f"\nREVENUE WRONG! Checking what's in sales accounts...")
    sa_rows = conn.execute("""
        SELECT ledger_name, mis_group, SUM(net) as total FROM pl_data
        WHERE company_id=2 AND LOWER(tally_group)='sales accounts'
          AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
        GROUP BY ledger_name, mis_group ORDER BY ABS(SUM(net)) DESC
    """).fetchall()
    for r in sa_rows:
        print(f"  ln='{r['ledger_name']}' mis='{r['mis_group']}' {r['total']/1e7:.4f}")

conn.close()
