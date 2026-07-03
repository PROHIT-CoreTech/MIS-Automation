"""Run: python check_mis_reports.py
Checks MIS Reports section_total values vs Tally for all 3 companies
"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

# Simulate exact reports.py section_total logic
def get_section_totals(cid, fy, fm, ty, tm):
    pl_rows = conn.execute("""
        SELECT ledger_name, mis_group, tally_group, year, month, net
        FROM pl_data WHERE company_id=?
          AND ((year>?) OR (year=? AND month>=?))
          AND ((year<?) OR (year=? AND month<=?))
    """, (cid,fy,fy,fm,ty,ty,tm)).fetchall()

    group_totals = {}
    data = {}
    TALLY_SECTION = {
        'sales accounts': 'revenue',
        'direct incomes': 'dir_inc',
        'opening stock':  'opening',
        'purchase accounts': 'purchases',
        'add: purchase accounts': 'purchases',
        'direct expenses': 'direct_exp',
        'less: closing stock': 'closing',
        'closing stock': 'closing',
        'cos_net': 'cos_net',
        'indirect incomes': 'ind_inc',
        'indirect expenses': 'overhead',
        'salaries and bonus': 'overhead',
    }

    for r in pl_rows:
        tg  = str(r['tally_group'] or '').lower().strip()
        mg  = str(r['mis_group']   or '').lower().strip()
        ln  = str(r['ledger_name'] or '').strip()
        yr  = int(r['year']); mo = int(r['month'])
        val = r['net'] or 0
        lbl = f"{MONTHS[mo-1]}-{str(yr)[2:]}"

        if tg in HEADERS or mg in HEADERS: continue

        # Group totals BEFORE skip
        if tg == 'indirect expenses' and ln.lower() == 'indirect expenses':
            group_totals.setdefault('overhead', {})
            group_totals['overhead'][lbl] = group_totals['overhead'].get(lbl,0) + val
            continue
        if tg == 'salaries and bonus' and ln.lower() == 'salaries and bonus':
            group_totals.setdefault('overhead_sal', {})
            group_totals['overhead_sal'][lbl] = group_totals['overhead_sal'].get(lbl,0) + val
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

    # Annual section totals
    def annual(sec_key):
        if sec_key == 'revenue':
            return abs(sum(group_totals.get('revenue',{}).values()))
        if sec_key == 'dir_inc':
            gt = abs(sum(group_totals.get('dir_inc_group',{}).values()))
            items = sum(abs(v) for mo_d in
                       [d for (s,t,l),d in data.items() if s=='dir_inc']
                       for v in mo_d.values())
            return max(gt, items)
        if sec_key == 'cogs':
            return abs(sum(group_totals.get('cogs',{}).values()))
        if sec_key == 'overhead':
            ie  = abs(sum(group_totals.get('overhead',{}).values()))
            sal = abs(sum(group_totals.get('overhead_sal',{}).values()))
            return ie + sal
        if sec_key == 'ind_inc':
            return sum(abs(v) for (s,t,l),d in data.items()
                      if s=='ind_inc' for v in d.values())
        return 0

    rev = annual('revenue')
    di  = annual('dir_inc')
    cos = annual('cogs')
    oh  = annual('overhead')
    ii  = annual('ind_inc')
    gp  = rev + di - cos
    np_ = gp + ii - oh
    return dict(rev=rev,di=di,cos=cos,gp=gp,ii=ii,oh=oh,np=np_)

TALLY = {
    2: dict(rev=68.00,gp=19.49,oh=7.20,np=12.44, label="USP FY25-26"),
    1: dict(rev=0.00, gp=-0.41,oh=2.23,np=-2.61, label="Intellichemie FY25-26"),
    3: dict(rev=27.91,gp=12.07,oh=6.15,np=5.93,  label="Avenuecorp FY25-26"),
}
PERIODS={2:(2025,4,2026,3),1:(2025,4,2026,3),3:(2025,4,2026,3)}

print("="*65)
print("MIS REPORTS section_total VERIFICATION")
print("="*65)
all_ok=True
for cid in [2,1,3]:
    t=TALLY[cid]; fy,fm,ty,tm=PERIODS[cid]
    p=get_section_totals(cid,fy,fm,ty,tm)
    print(f"\n  {t['label']}")
    print(f"  {'':10s} {'REPORTS':>10s}  {'TALLY':>10s}  {'DIFF':>8s}  STATUS")
    print("  "+"-"*48)
    for name,pv,tv in [
        ('Revenue', p['rev']/1e7, t['rev']),
        ('GP',      p['gp']/1e7,  t['gp']),
        ('Overhead',p['oh']/1e7,  t['oh']),
        ('NP',      p['np']/1e7,  t['np']),
    ]:
        if tv==0 and pv==0: continue
        d=pv-tv
        ok='✅' if abs(d)<0.05 else ('🟡' if abs(d)<0.15 else '❌')
        if abs(d)>=0.05: all_ok=False
        print(f"  {name:10s} {pv:>10.4f}  {tv:>10.4f}  {d:>+8.4f}  {ok}")

print(f"\n{'='*65}")
print(f"RESULT: {'✅ ALL PASS' if all_ok else '⚠️  CHECK ABOVE'}")
conn.close()
