"""Run: python debug_avenuecorp_calc.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

rows = conn.execute("""
    SELECT ledger_name, mis_group, tally_group, net
    FROM pl_data WHERE company_id=3
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchall()
print(f"FY25-26 rows: {len(rows)}")

rev=dir_g=dir_i=cos=oh_grp=oh_sal=oh_items=ind_inc=0
cos_found=oh_found=False
rev_detail = {}

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
        rev_detail[r['ledger_name']] = rev_detail.get(r['ledger_name'],0) + (r['net'] or 0)
        if mg == 'sales accounts': rev += v
    elif tg == 'direct incomes':
        if mg == 'direct incomes': dir_g += v
        else: dir_i += v
    elif tg == 'cost of sales :':
        cos += v; cos_found=True
    elif tg == 'indirect incomes':
        ind_inc += v
    elif tg == 'salaries and bonus':
        oh_sal += v
    elif tg in ('indirect expenses','salary accounts'):
        oh_items += v

dir_inc  = dir_g if dir_g else dir_i
overhead = (oh_grp if oh_found else oh_items) + oh_sal
cogs     = cos if cos_found else 0
gp       = rev + dir_inc - cogs
np_      = gp + ind_inc - overhead

print(f"\nSales Accounts breakdown:")
for k,v2 in sorted(rev_detail.items(), key=lambda x: -abs(x[1])):
    print(f"  '{k}' mis check: ", end='')
    # check mis_group
    mg_row = conn.execute("""
        SELECT mis_group FROM pl_data WHERE company_id=3
        AND ledger_name=? AND tally_group='Sales Accounts' LIMIT 1
    """, (k,)).fetchone()
    mg_val = mg_row['mis_group'] if mg_row else 'N/A'
    counted = '✅ COUNTED' if mg_val == 'Sales Accounts' else '❌ SKIPPED'
    print(f"mis='{mg_val}' {counted}  val={v2/1e7:.4f}Cr")

print(f"\nrev_total = {rev/1e7:.4f} Cr  (expected 27.91)")
print(f"  → group total row ('Sales Accounts') mis_group check:")
sa_row = conn.execute("""
    SELECT mis_group, SUM(net) as total FROM pl_data
    WHERE company_id=3 AND tally_group='Sales Accounts'
      AND ledger_name='Sales Accounts'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY mis_group
""").fetchall()
for r in sa_row:
    print(f"    mis='{r['mis_group']}' total={r['total']/1e7:.4f}Cr")

print(f"\nCOGS: cos_found={cos_found} cos={cogs/1e7:.4f}Cr")
print(f"GP  = {gp/1e7:.4f}Cr  (Tally=12.07)")
print(f"OH  = {overhead/1e7:.4f}Cr  (Tally=6.15, IE={oh_grp/1e7:.2f}+Sal={oh_sal/1e7:.2f})")
print(f"NP  = {np_/1e7:.4f}Cr  (Tally=5.93)")
conn.close()
