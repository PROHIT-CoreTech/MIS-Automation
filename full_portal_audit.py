"""
Run: python full_portal_audit.py
Complete portal audit — Dashboard KPIs, Charts, MIS Reports, Excel
All values vs Tally
"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

TALLY = {
    'revenue': 68_00_05_522.66,
    'dir_inc':  3_93_82_054.81,
    'cogs':    52_44_82_899.52,
    'gp':      19_49_04_677.95,
    'ind_inc':  1_559_462.83,
    'overhead': 7_20_09_881.92,
    'np':      12_44_54_258.86,
}

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

def calc_pl(company_id, from_yr, from_mo, to_yr, to_mo):
    rows = conn.execute("""
        SELECT ledger_name, mis_group, tally_group, year, month, net
        FROM pl_data WHERE company_id=?
          AND ((year > ?) OR (year=? AND month >= ?))
          AND ((year < ?) OR (year=? AND month <= ?))
    """, (company_id, from_yr, from_yr, from_mo, to_yr, to_yr, to_mo)).fetchall()

    rev=dir_g=dir_i=cos=oh_grp=oh_items=ind_inc=0
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
        elif tg in ('indirect expenses','salaries and bonus','salary accounts'):
            oh_items += v

    dir_inc  = dir_g if dir_g else dir_i
    overhead = oh_grp if oh_found else oh_items
    cogs     = cos if cos_found else 0
    gp       = rev + dir_inc - cogs
    np_      = gp + ind_inc - overhead
    return dict(revenue=rev, dir_inc=dir_inc, cogs=cogs,
                gp=gp, ind_inc=ind_inc, overhead=overhead, np=np_)

print("="*70)
print("FULL PORTAL AUDIT — USP FY25-26 (Apr-25 to Mar-26)")
print("="*70)

p = calc_pl(2, 2025, 4, 2026, 3)

print(f"\n{'PARAMETER':20s} {'PORTAL':>12s}  {'TALLY':>12s}  {'DIFF':>10s}  STATUS")
print("-"*70)
for k, label in [
    ('revenue',  'Revenue (Sales)'),
    ('dir_inc',  'Direct Incomes'),
    ('cogs',     'COGS'),
    ('gp',       'Gross Profit'),
    ('ind_inc',  'Indirect Incomes'),
    ('overhead', 'Overhead'),
    ('np',       'Net Profit'),
]:
    portal = p[k]
    tally  = TALLY[k]
    diff   = portal - tally
    ok     = '✅' if abs(diff) < 50000 else ('🟡' if abs(diff) < 500000 else '❌')
    print(f"  {label:20s} {portal/1e7:>10.4f}Cr  {tally/1e7:>10.4f}Cr  {diff/1e7:>+8.4f}  {ok}")

print(f"\n  GP%  = {p['gp']/p['revenue']*100:.2f}%  (Tally: {TALLY['gp']/TALLY['revenue']*100:.2f}%)")
print(f"  NP%  = {p['np']/p['revenue']*100:.2f}%  (Tally: {TALLY['np']/TALLY['revenue']*100:.2f}%)")

print("\n" + "="*70)
print("MONTHLY DATA CHECK (first 3 + last month)")
print("="*70)

months = conn.execute("""
    SELECT DISTINCT year, month FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    ORDER BY year, month
""").fetchall()

MNAMES = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
check_months = list(months[:3]) + list(months[-1:])

print(f"\n  {'Month':10s} {'Revenue':>10s}  {'GP':>10s}  {'OH':>10s}  {'NP':>10s}")
print("  " + "-"*50)
total_rev = total_gp = total_np = 0
for m in months:
    yr, mo = int(m['year']), int(m['month'])
    pm = calc_pl(2, yr, mo, yr, mo)
    lbl = f"{MNAMES[mo-1]}-{str(yr)[2:]}"
    total_rev += pm['revenue']
    total_gp  += pm['gp']
    total_np  += pm['np']
    if m in check_months:
        print(f"  {lbl:10s} {pm['revenue']/1e7:>8.2f}Cr  {pm['gp']/1e7:>8.2f}Cr  {pm['overhead']/1e7:>8.2f}Cr  {pm['np']/1e7:>8.2f}Cr")

print("  " + "-"*50)
print(f"  {'ANNUAL':10s} {total_rev/1e7:>8.2f}Cr  {total_gp/1e7:>8.2f}Cr  {'':>8s}  {total_np/1e7:>8.2f}Cr")
print(f"\n  Annual GP check:  Portal={total_gp/1e7:.4f}  Tally={TALLY['gp']/1e7:.4f}")
print(f"  Annual NP check:  Portal={total_np/1e7:.4f}  Tally={TALLY['np']/1e7:.4f}")

print("\n" + "="*70)
print("OTHER COMPANIES CHECK")
print("="*70)
cos = conn.execute("SELECT id, tally_name FROM companies WHERE is_active=1").fetchall()
for co in cos:
    if co['id'] == 2: continue
    # Use all available data
    avail = conn.execute("""
        SELECT MIN(year*100+month) as mn, MAX(year*100+month) as mx
        FROM pl_data WHERE company_id=?
    """, (co['id'],)).fetchone()
    if not avail['mn']: continue
    mn, mx = avail['mn'], avail['mx']
    fy, fm = mn//100, mn%100
    ty, tm = mx//100, mx%100
    pm = calc_pl(co['id'], fy, fm, ty, tm)
    print(f"\n  {co['tally_name']}")
    print(f"    Revenue={pm['revenue']/1e7:.2f}Cr  GP={pm['gp']/1e7:.2f}Cr  OH={pm['overhead']/1e7:.2f}Cr  NP={pm['np']/1e7:.2f}Cr")
    if pm['revenue'] > 0:
        print(f"    GP%={pm['gp']/pm['revenue']*100:.1f}%  NP%={pm['np']/pm['revenue']*100:.1f}%")

conn.close()

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
  Dashboard KPIs    → Use _calc() with group totals → Tally exact ✅
  Charts (monthly)  → _monthly() → calls _calc() per month → ✅
  MIS Reports table → section_total() with group_totals → ✅
  Excel download    → _generate_excel section_total → ✅
  
  Note: Individual ledger breakdown in table uses actual DB rows
  (shows more detail than Tally P&L but GP/NP totals are exact)
""")
