"""Run: python verify_avenuecorp_fy2324.py
Avenuecorp FY 23-24 = Apr-23 to Mar-24 (as per company name)
But Tally screenshot shows 1-Apr-25 to 31-Mar-26 — check which period is correct
"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

def calc(cid, from_yr, from_mo, to_yr, to_mo):
    rows = conn.execute("""
        SELECT ledger_name, mis_group, tally_group, net
        FROM pl_data WHERE company_id=?
          AND ((year > ?) OR (year=? AND month >= ?))
          AND ((year < ?) OR (year=? AND month <= ?))
    """, (cid, from_yr, from_yr, from_mo, to_yr, to_yr, to_mo)).fetchall()

    rev=dir_g=dir_i=cos=oh_grp=oh_sal=oh_items=ind_inc=0
    cos_found=oh_found=False

    for r in rows:
        tg=str(r['tally_group'] or '').lower().strip()
        mg=str(r['mis_group']   or '').lower().strip()
        ln=str(r['ledger_name'] or '').lower().strip()
        v =abs(r['net'] or 0)

        if tg in HEADERS or mg in HEADERS: continue
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
        elif tg == 'salaries and bonus':
            oh_sal += v  # separate salary group
        elif tg in ('indirect expenses','salary accounts'):
            oh_items += v

    dir_inc  = dir_g if dir_g else dir_i
    overhead = (oh_grp if oh_found else oh_items) + oh_sal
    cogs     = cos if cos_found else 0
    gp       = rev + dir_inc - cogs
    np_      = gp + ind_inc - overhead
    return dict(rev=rev, dir_inc=dir_inc, cogs=cogs, gp=gp,
                ind_inc=ind_inc, overhead=overhead, np=np_,
                oh_grp=oh_grp, oh_sal=oh_sal)

# Tally screenshot says "1-Apr-25 to 31-Mar-26" but company name says "FY 23-24"
# Try both periods
print("="*70)
print("PERIOD ANALYSIS")
print("="*70)

periods = [
    ("FY 23-24 (Apr-23 to Mar-24)", 2023, 4, 2024, 3),
    ("FY 24-25 (Apr-24 to Mar-25)", 2024, 4, 2025, 3),
    ("FY 25-26 (Apr-25 to Mar-26)", 2025, 4, 2026, 3),
    ("All data",                    2023, 4, 2026, 6),
]

TALLY_REV = 27_90_82_711.93
TALLY_GP  = 12_07_37_877.00
TALLY_NP  =  5_93_09_000.66

for label, fy, fm, ty, tm in periods:
    p = calc(3, fy, fm, ty, tm)
    rev_diff = abs(p['rev'] - TALLY_REV)/1e7
    print(f"\n  {label}")
    print(f"    Revenue = {p['rev']/1e7:.2f}Cr  GP = {p['gp']/1e7:.2f}Cr  NP = {p['np']/1e7:.2f}Cr")
    print(f"    OH = {p['overhead']/1e7:.2f}Cr (IE={p['oh_grp']/1e7:.2f} + Sal={p['oh_sal']/1e7:.2f})")
    match = '✅ MATCH' if rev_diff < 0.5 else f'❌ diff={rev_diff:.2f}Cr'
    print(f"    vs Tally Rev={TALLY_REV/1e7:.2f} GP={TALLY_GP/1e7:.2f} NP={TALLY_NP/1e7:.2f} → {match}")

conn.close()
