"""Run: python trace_av_dirinc.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== All tg='direct incomes' rows for Avenuecorp FY25-26 ===")
rows = conn.execute("""
    SELECT ledger_name, tally_group, mis_group,
           SUM(net) as total, COUNT(*) as cnt
    FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='direct incomes'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, tally_group, mis_group
    ORDER BY ABS(SUM(net)) DESC
""").fetchall()

dir_total = 0
for r in rows:
    ln_lower = str(r['ledger_name']).lower().strip()
    tg_lower = 'direct incomes'
    is_grp = '← GROUP TOTAL' if ln_lower == tg_lower else ''
    print(f"  '{r['ledger_name']}' mis='{r['mis_group']}' {r['total']/1e7:.4f}Cr {is_grp}")
    if ln_lower == tg_lower:
        dir_total += (r['total'] or 0)

print(f"\ndir_inc_total (group total rows sum) = {dir_total/1e7:.4f} Cr")

# Now check cos_net accumulation
print("\n=== Cost of Sales monthly for Avenuecorp ===")
cos_rows = conn.execute("""
    SELECT year, month, net FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='cost of sales :'
      AND LOWER(ledger_name)='cost of sales :'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    ORDER BY year, month
""").fetchall()

cos_net = 0
for r in cos_rows:
    cos_net += (r['net'] or 0)
    print(f"  {r['year']}-{r['month']:02d}: net={r['net']/1e7:.4f}")
print(f"\nSUM(net) = {cos_net/1e7:.4f}  abs = {abs(cos_net)/1e7:.4f}")

# Simulate _calc
print("\n=== Simulating new _calc ===")
all_rows = conn.execute("""
    SELECT ledger_name, mis_group, tally_group, net FROM pl_data
    WHERE company_id=3
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchall()

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

rev=dit=dii=cos=ohg=ohs=ohi=ii=0
cf=of=osf=False
for r in all_rows:
    tg=str(r['tally_group'] or '').lower().strip()
    mg=str(r['mis_group']   or '').lower().strip()
    ln=str(r['ledger_name'] or '').lower().strip()
    net=r['net'] or 0; v=abs(net)
    if tg in HEADERS or mg in HEADERS: continue
    if tg=='indirect expenses' and ln=='indirect expenses': ohg+=net;of=True;continue
    if tg=='salaries and bonus' and ln=='salaries and bonus': ohs+=net;osf=True;continue
    if tg=='cost of sales :' and ln=='cost of sales :': cos+=net;cf=True;continue
    if tg=='sales accounts' and ln=='sales accounts': rev+=net;continue
    if tg=='direct incomes' and ln=='direct incomes': dit+=net;continue
    if mg=='_group_total_': continue
    if ln==tg: continue
    if tg=='direct incomes': dii+=v
    elif tg=='indirect incomes': ii+=v

dir_inc=abs(dit) if dit else abs(dii)
overhead=(abs(ohg)+abs(ohs)) if (of or osf) else ohi
cogs=abs(cos) if cf else 0
gp=abs(rev)+dir_inc-cogs
np_=gp+ii-overhead

print(f"rev={abs(rev)/1e7:.4f} dit={dit/1e7:.4f} dii={dii/1e7:.4f}")
print(f"dir_inc={dir_inc/1e7:.4f} cogs={cogs/1e7:.4f}")
print(f"GP={gp/1e7:.4f}  Expected=12.07")
conn.close()
