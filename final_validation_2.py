"""Run: python final_validation.py"""
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
    """, (cid,fy,fy,fm,ty,ty,tm)).fetchall()

    rev=dir_g=dir_i=cos=oh_grp=oh_sal=oh_items=ind_inc=0
    cos_found=oh_found=oh_sal_found=False

    for r in rows:
        tg=str(r['tally_group'] or '').lower().strip()
        mg=str(r['mis_group']   or '').lower().strip()
        ln=str(r['ledger_name'] or '').lower().strip()
        net=r['net'] or 0
        v  =abs(net)

        if tg in HEADERS or mg in HEADERS: continue

        # Group totals BEFORE skip — use abs(net) for expenses, net for COGS
        if tg == 'indirect expenses' and ln == 'indirect expenses':
            oh_grp += v; oh_found=True; continue
        if tg == 'salaries and bonus' and ln == 'salaries and bonus':
            oh_sal += v; oh_sal_found=True; continue
        if tg == 'cost of sales :' and ln == 'cost of sales :':
            cos += net; cos_found=True; continue  # net (can be +/-)
        if tg == 'sales accounts' and ln == 'sales accounts':
            rev += v; continue
        if tg == 'direct incomes' and ln == 'direct incomes':
            dir_g += v; continue

        if mg == '_group_total_': continue
        if ln == tg: continue

        if tg == 'direct incomes':    dir_i   += v
        elif tg == 'indirect incomes': ind_inc += v
        elif tg in ('indirect expenses','salaries and bonus','salary accounts'):
            oh_items += v

    dir_inc  = dir_g if dir_g else dir_i
    overhead = (oh_grp + oh_sal) if (oh_found or oh_sal_found) else oh_items
    cogs     = abs(cos) if cos_found else 0
    gp       = rev + dir_inc - cogs
    np_      = gp + ind_inc - overhead
    return dict(rev=rev, gp=gp, oh=overhead, np=np_,
                oh_ie=oh_grp, oh_sal=oh_sal, cogs=cogs)

TALLY = {
    2: dict(rev=68.00,  gp=19.49, oh=7.20, np=12.44,  label="USP FY25-26"),
    1: dict(rev=0.00,   gp=-0.41, oh=2.23, np=-2.61,  label="Intellichemie FY25-26"),
    3: dict(rev=27.91,  gp=12.07, oh=6.15, np=5.93,   label="Avenuecorp FY25-26"),
}
PERIODS = {2:(2025,4,2026,3), 1:(2025,4,2026,3), 3:(2025,4,2026,3)}

print("="*65)
print("FINAL VALIDATION — ALL 3 COMPANIES")
print("="*65)
all_ok = True
for cid in [2,1,3]:
    t = TALLY[cid]; fy,fm,ty,tm = PERIODS[cid]
    p = calc(cid,fy,fm,ty,tm)
    print(f"\n  {t['label']}")
    print(f"  {'':10s} {'PORTAL':>10s}  {'TALLY':>10s}  {'DIFF':>8s}  STATUS")
    print("  "+"-"*48)
    for name,pv,tv in [
        ('Revenue', p['rev']/1e7, t['rev']),
        ('GP',      p['gp']/1e7,  t['gp']),
        ('Overhead',p['oh']/1e7,  t['oh']),
        ('NP',      p['np']/1e7,  t['np']),
    ]:
        d=pv-tv
        ok='✅' if abs(d)<0.05 else ('🟡' if abs(d)<0.15 else '❌')
        if abs(d)>=0.05: all_ok=False
        print(f"  {name:10s} {pv:>10.4f}  {tv:>10.4f}  {d:>+8.4f}  {ok}")
    print(f"  COGS={p['cogs']/1e7:.4f} IE={p['oh_ie']/1e7:.4f} Sal={p['oh_sal']/1e7:.4f}")

print(f"\n{'='*65}")
print(f"RESULT: {'✅ ALL PASS' if all_ok else '⚠️  CHECK ABOVE'}")
conn.close()
