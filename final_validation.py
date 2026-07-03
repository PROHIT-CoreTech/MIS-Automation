"""Run: python final_validation.py — All 3 companies final check"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

def calc(cid, fy, fm, ty, tm):
    rows = conn.execute("""
        SELECT ledger_name, mis_group, tally_group, net FROM pl_data
        WHERE company_id=?
          AND ((year>?) OR (year=? AND month>=?))
          AND ((year<?) OR (year=? AND month<=?))
    """, (cid, fy, fy, fm, ty, ty, tm)).fetchall()

    rev=dir_g=dir_i=cos=oh_grp=oh_sal_grp=oh_items=ind_inc=0
    cos_found=oh_found=oh_sal_found=False

    for r in rows:
        tg=str(r['tally_group'] or '').lower().strip()
        mg=str(r['mis_group']   or '').lower().strip()
        ln=str(r['ledger_name'] or '').lower().strip()
        v =abs(r['net'] or 0)
        if tg in HEADERS or mg in HEADERS: continue
        if tg == 'indirect expenses' and ln == 'indirect expenses':
            oh_grp += v; oh_found=True; continue
        if tg == 'salaries and bonus' and ln == 'salaries and bonus':
            oh_sal_grp += v; oh_sal_found=True; continue
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
    overhead = (oh_grp + oh_sal_grp) if (oh_found or oh_sal_found) else oh_items
    cogs     = cos if cos_found else 0
    gp       = rev + dir_inc - cogs
    np_      = gp + ind_inc - overhead
    return dict(rev=rev, gp=gp, overhead=overhead, np=np_,
                oh_grp=oh_grp, oh_sal=oh_sal_grp)

TALLY = {
    'USP':   dict(rev=68.00,  gp=19.49, oh=7.20,  np=12.44),
    'Intel': dict(rev=0.00,   gp=-0.41, oh=22.30, np=-26.10),
    'Avenu': dict(rev=27.91,  gp=12.07, oh=6.15,  np=5.93),
}

tests = [
    ("USP FY25-26",         2, 2025,4,2026,3, TALLY['USP']),
    ("Intellichemie FY25-26",1, 2025,4,2026,3, TALLY['Intel']),
    ("Avenuecorp FY25-26",  3, 2025,4,2026,3, TALLY['Avenu']),
]

print("="*70)
print("FINAL VALIDATION — ALL COMPANIES")
print("="*70)

all_ok = True
for label, cid, fy,fm,ty,tm, tally in tests:
    p = calc(cid, fy, fm, ty, tm)
    print(f"\n  {label}")
    print(f"  {'':10s} {'PORTAL':>10s}  {'TALLY':>10s}  {'DIFF':>8s}  STATUS")
    print("  " + "-"*48)
    for name, pv, tv in [
        ('Revenue',  p['rev']/1e7,      tally['rev']),
        ('GP',       p['gp']/1e7,       tally['gp']),
        ('Overhead', p['overhead']/1e7, tally['oh']),
        ('NP',       p['np']/1e7,       tally['np']),
    ]:
        diff = pv - tv
        ok = '✅' if abs(diff)<0.05 else ('🟡' if abs(diff)<0.50 else '❌')
        if abs(diff) >= 0.05: all_ok = False
        print(f"  {name:10s} {pv:>10.2f}  {tv:>10.2f}  {diff:>+8.2f}  {ok}")
    print(f"  OH breakdown: IE={p['oh_grp']/1e7:.2f} + Sal={p['oh_sal']/1e7:.2f} = {p['overhead']/1e7:.2f}")

print(f"\n{'='*70}")
print(f"OVERALL: {'✅ ALL PASS' if all_ok else '❌ SOME ISSUES'}")
print(f"{'='*70}")
conn.close()
