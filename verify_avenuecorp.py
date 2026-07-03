"""Run: python verify_avenuecorp.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

# Avenuecorp = company_id=3, FY23-24 = Apr-23 to Mar-24
rows = conn.execute("""
    SELECT ledger_name, mis_group, tally_group, net
    FROM pl_data WHERE company_id=3
      AND ((year=2023 AND month>=4) OR (year=2024 AND month<=3))
""").fetchall()

print(f"Total rows: {len(rows)}")

rev=dir_g=dir_i=cos=oh_grp=oh_items=ind_inc=0
cos_found=oh_found=False

for r in rows:
    tg=str(r['tally_group'] or '').lower().strip()
    mg=str(r['mis_group']   or '').lower().strip()
    ln=str(r['ledger_name'] or '').lower().strip()
    v =abs(r['net'] or 0)

    if tg in HEADERS or mg in HEADERS: continue

    # Capture overhead group total FIRST
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

print(f"\nAVENUECORP FY23-24 — _calc simulation")
print(f"  Revenue  = {rev/1e7:.4f} Cr")
print(f"  Dir Inc  = {dir_inc/1e7:.4f} Cr")
print(f"  COGS     = {cogs/1e7:.4f} Cr")
print(f"  GP       = {gp/1e7:.4f} Cr")
print(f"  Ind Inc  = {ind_inc/1e7:.4f} Cr")
print(f"  Overhead = {overhead/1e7:.4f} Cr  (group total used: {oh_found})")
print(f"  NP       = {np_/1e7:.4f} Cr")
print(f"\n  oh_grp (IE group total)  = {oh_grp/1e7:.4f} Cr")
print(f"  oh_items (individual sum) = {oh_items/1e7:.4f} Cr")
print(f"\n  NOTE: 'Salaries and Bonus' group total = _GROUP_TOTAL_ tagged → SKIPPED")
print(f"  Individual salary rows counted separately")

# Check Salaries
sal = conn.execute("""
    SELECT mis_group, SUM(net) as total, COUNT(*) as cnt
    FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='salaries and bonus'
      AND ((year=2023 AND month>=4) OR (year=2024 AND month<=3))
    GROUP BY mis_group
""").fetchall()
print(f"\n  Salaries breakdown:")
for r in sal:
    print(f"    mis='{r['mis_group']}' total={r['total']/1e7:.4f}Cr cnt={r['cnt']}")

# Check Indirect Expenses group total
ie = conn.execute("""
    SELECT SUM(net) as total FROM pl_data
    WHERE company_id=3
      AND LOWER(tally_group)='indirect expenses'
      AND LOWER(ledger_name)='indirect expenses'
      AND ((year=2023 AND month>=4) OR (year=2024 AND month<=3))
""").fetchone()
print(f"\n  IE group total (FY23-24) = {(ie['total'] or 0)/1e7:.4f} Cr")
print(f"  This includes Salaries+Bonus in Tally's calculation")

conn.close()
