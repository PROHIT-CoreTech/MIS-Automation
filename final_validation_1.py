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
    """, (cid, fy,fy,fm, ty,ty,tm)).fetchall()

    rev=dir_g=dir_i=cos=oh_grp=oh_sal_grp=oh_items=ind_inc=0
    cos_found=oh_found=oh_sal_found=False

    for r in rows:
        tg=str(r['tally_group'] or '').lower().strip()
        mg=str(r['mis_group']   or '').lower().strip()
        ln=str(r['ledger_name'] or '').lower().strip()
        val     = abs(r['net'] or 0)
        net_val = r['net'] or 0

        if tg in HEADERS or mg in HEADERS: continue

        # Capture group totals BEFORE any skip
        if tg == 'indirect expenses' and ln == 'indirect expenses':
            oh_grp += val; oh_found=True; continue
        if tg == 'salaries and bonus' and ln == 'salaries and bonus':
            oh_sal_grp += val; oh_sal_found=True; continue
        # COGS: use net_val (sum of monthly net gives correct annual COGS)
        if tg == 'cost of sales :' and ln == 'cost of sales :':
            cos += net_val; cos_found=True; continue
        if tg == 'sales accounts' and ln == 'sales accounts':
            rev += val; continue
        if tg == 'direct incomes' and ln == 'direct incomes':
            dir_g += val; continue

        if mg == '_group_total_': continue
        if ln == tg: continue

        if tg == 'direct incomes': dir_i += val
        elif tg == 'indirect incomes': ind_inc += val
        elif tg in ('indirect expenses','salaries and bonus','salary accounts'):
            oh_items += val

    dir_inc  = dir_g if dir_g else dir_i
    overhead = (oh_grp + oh_sal_grp) if (oh_found or oh_sal_found) else oh_items
    cogs     = abs(cos) if cos_found else 0
    gp       = rev + dir_inc - cogs
    np_      = gp + ind_inc - overhead
    return dict(rev=rev, gp=gp, overhead=overhead, np=np_,
                oh_grp=oh_grp, oh_sal=oh_sal_grp, cogs=cogs,
                dir_inc=dir_inc, ind_inc=ind_inc)

# Correct Tally values (Indian notation verified)
TALLY = {
    'USP':   dict(rev=68.00,  gp=19.49, oh=7.20,  np=12.44),
    'Intel': dict(rev=0.00,   gp=-0.41, oh=2.23,  np=-2.61),
    'Avenu': dict(rev=27.91,  gp=12.07, oh=6.15,  np=5.93),
}
tests = [
    ("USP FY25-26",          2, 2025,4,2026,3, TALLY['USP']),
    ("Intellichemie FY25-26",1, 2025,4,2026,3, TALLY['Intel']),
    ("Avenuecorp FY25-26",   3, 2025,4,2026,3, TALLY['Avenu']),
]

print("="*70)
print("FINAL VALIDATION v3 — ALL COMPANIES")
print("="*70)

all_ok = True
for label, cid, fy,fm,ty,tm, tally in tests:
    p = calc(cid, fy, fm, ty, tm)
    print(f"\n  {label}")
    print(f"  {'':10s} {'PORTAL':>10s}  {'TALLY':>10s}  {'DIFF':>8s}  STATUS")
    print("  " + "-"*50)
    for name, pv, tv in [
        ('Revenue',  p['rev']/1e7,      tally['rev']),
        ('GP',       p['gp']/1e7,       tally['gp']),
        ('Overhead', p['overhead']/1e7, tally['oh']),
        ('NP',       p['np']/1e7,       tally['np']),
    ]:
        diff = pv - tv
        ok = '✅' if abs(diff)<0.05 else ('🟡' if abs(diff)<0.50 else '❌')
        if abs(diff) >= 0.05: all_ok = False
        print(f"  {name:10s} {pv:>10.4f}  {tv:>10.4f}  {diff:>+8.4f}  {ok}")
    print(f"  COGS={p['cogs']/1e7:.4f} DirInc={p['dir_inc']/1e7:.4f} IndInc={p['ind_inc']/1e7:.4f}")
    print(f"  OH: IE={p['oh_grp']/1e7:.4f} + Sal={p['oh_sal']/1e7:.4f} = {p['overhead']/1e7:.4f}")

print(f"\n{'='*70}")
print(f"RESULT: {'✅ ALL PASS' if all_ok else '⚠️ CHECK ABOVE'}")
conn.close()
