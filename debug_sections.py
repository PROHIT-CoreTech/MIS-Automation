"""Run: python debug_sections.py"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
TALLY_SECTION = {
    'sales accounts': 'revenue', 'direct incomes': 'dir_inc',
    'opening stock': 'opening', 'purchase accounts': 'purchases',
    'add: purchase accounts': 'purchases', 'direct expenses': 'direct_exp',
    'less: closing stock': 'closing', 'closing stock': 'closing',
    'cost of sales :': 'cos_net', 'indirect incomes': 'ind_inc',
    'indirect expenses': 'overhead', 'salaries and bonus': 'overhead',
    'salary accounts': 'overhead',
}
HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

pl_rows = conn.execute("""
    SELECT ledger_name, mis_group, tally_group, year, month, net
    FROM pl_data WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchall()

data = {}
group_totals = {}

for r in pl_rows:
    tg  = str(r['tally_group'] or '').lower().strip()
    mg  = str(r['mis_group']   or '').lower().strip()
    ln  = str(r['ledger_name'] or '').strip()
    yr  = int(r['year']); mo = int(r['month'])
    val = r['net'] or 0
    lbl = f"{MONTHS[mo-1]}-{str(yr)[2:]}"

    if tg in HEADERS or mg in HEADERS: continue
    if tg == 'indirect expenses' and ln.lower() == 'indirect expenses':
        group_totals.setdefault('overhead', {})
        group_totals['overhead'][lbl] = group_totals['overhead'].get(lbl, 0) + val
        continue
    if tg == 'salaries and bonus' and ln.lower() == 'salaries and bonus':
        group_totals.setdefault('overhead_sal', {})
        group_totals['overhead_sal'][lbl] = group_totals['overhead_sal'].get(lbl, 0) + val
        continue
    if mg == '_group_total_': continue
    if ln.lower() == tg:
        if tg == 'sales accounts':
            group_totals.setdefault('revenue', {})
            group_totals['revenue'][lbl] = group_totals['revenue'].get(lbl,0) + val
        elif tg == 'direct incomes':
            group_totals.setdefault('dir_inc_group', {})
            group_totals['dir_inc_group'][lbl] = group_totals['dir_inc_group'].get(lbl,0) + val
        elif tg == 'cost of sales :':
            group_totals.setdefault('cogs', {})
            group_totals['cogs'][lbl] = group_totals['cogs'].get(lbl,0) + val
        continue
    sec = TALLY_SECTION.get(tg)
    if not sec: continue
    key = (sec, tg, ln)
    if key not in data: data[key] = {}
    data[key][(yr,mo)] = data[key].get((yr,mo),0) + val

# Build sections
sections = {'revenue':{},'dir_inc':{},'opening':{},'purchases':{},
            'direct_exp':{},'closing':{},'cos_net':{},'ind_inc':{},'overhead':{}}
for (sec,tg,ln),mo_data in data.items():
    if sec not in sections: continue
    if ln not in sections[sec]: sections[sec][ln] = {}
    for (yr,mo),val in mo_data.items():
        lbl = f"{MONTHS[mo-1]}-{str(yr)[2:]}"
        sections[sec][ln][lbl] = sections[sec][ln].get(lbl,0) + val

print("=== SECTIONS SUMMARY ===")
for k,v in sections.items():
    total = sum(abs(vv) for d in v.values() for vv in d.values())
    print(f"  '{k}': {len(v)} ledgers, total={total/1e7:.4f} Cr")

print(f"\n=== GROUP TOTALS ===")
for k,v in group_totals.items():
    total = abs(sum(v.values()))
    print(f"  '{k}': total={total/1e7:.4f} Cr")

print(f"\n=== COGS check ===")
print(f"  'cogs' in group_totals: {'cogs' in group_totals}")
if 'cogs' in group_totals:
    print(f"  Annual COGS = {abs(sum(group_totals['cogs'].values()))/1e7:.4f} Cr")

conn.close()
