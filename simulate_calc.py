"""
Run: python simulate_calc.py
Exact simulation of dashboard _calc for USP Apr-25 to Mar-26
Shows exact overhead composition
"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

rows = conn.execute("""
    SELECT ledger_name, mis_group, tally_group, year, month, net
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    ORDER BY year, month
""").fetchall()

print(f"Total rows: {len(rows)}")

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

rev_total=dir_inc_total=dir_inc_items=cos_net=ind_inc=overhead=0
cos_net_found=False
oh_detail = {}

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
        cos_net += val; cos_net_found=True; continue
    if tg == 'indirect incomes':
        ind_inc += val; continue
    if tg in ('indirect expenses','salaries and bonus','salary accounts'):
        overhead += val
        oh_detail[r['ledger_name']] = oh_detail.get(r['ledger_name'],0) + val
        continue

dir_inc = dir_inc_total if dir_inc_total else dir_inc_items
cogs = cos_net if cos_net_found else 0
gp   = rev_total + dir_inc - cogs
np_  = gp + ind_inc - overhead

print(f"\nRevenue   = {rev_total/1e7:.4f} Cr")
print(f"Dir Inc   = {dir_inc/1e7:.4f} Cr")
print(f"COGS      = {cogs/1e7:.4f} Cr")
print(f"GP        = {gp/1e7:.4f} Cr")
print(f"Ind Inc   = {ind_inc/1e7:.4f} Cr")
print(f"Overhead  = {overhead/1e7:.4f} Cr")
print(f"NP        = {np_/1e7:.4f} Cr")

print(f"\nOverhead breakdown (top items):")
for k,v in sorted(oh_detail.items(), key=lambda x:-x[1])[:15]:
    print(f"  {k:45s} {v/1e7:.4f} Cr")

print(f"\nTally:  GP=19.49, OH=7.20, NP=12.44")
print(f"Portal: GP={gp/1e7:.2f}, OH={overhead/1e7:.2f}, NP={np_/1e7:.2f}")
print(f"OH diff = {overhead/1e7 - 7.20:.4f} Cr")
print(f"NP diff = {np_/1e7 - 12.44:.4f} Cr")

conn.close()
