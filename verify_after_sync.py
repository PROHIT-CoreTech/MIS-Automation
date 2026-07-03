"""
Run AFTER sync: python verify_after_sync.py
Checks if new ledgers came in and P&L still matches Tally
"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== POST-SYNC VERIFICATION ===\n")

# Check new ledgers
new_ledgers = [
    "IGST Purchase @18%", "Local GST Purchase @ 18 %",
    "Purchase - GST (Local)", "Purchase - IGST (Inter State)",
    "Purchase - Import", "Purchase Bills to Come",
    "Opening Stock", "Salaries & Wages",
    "Co's Contribution to EPFO", "Co's Contribution to ESIC",
    "Freight & Clearing Agent Charges - Import",
]

print("1. NEW LEDGERS CHECK:")
for ln in new_ledgers:
    r = conn.execute("""
        SELECT SUM(net) as total FROM pl_data
        WHERE company_id=2 AND ledger_name=?
          AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    """, (ln,)).fetchone()
    val = r['total'] or 0
    status = f"✅ {val/1e7:.4f} Cr" if val != 0 else "❌ Still missing"
    print(f"  {ln:45s} {status}")

# Full P&L check
print("\n2. P&L VERIFICATION:")
rows = conn.execute("""
    SELECT ledger_name, mis_group, tally_group, net
    FROM pl_data WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchall()

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

rev=dir_g=dir_i=cos=oh_grp=oh_items=ind_inc=0
cos_found=oh_found=False

for r in rows:
    tg = str(r['tally_group'] or '').lower().strip()
    mg = str(r['mis_group']   or '').lower().strip()
    ln = str(r['ledger_name'] or '').lower().strip()
    v  = abs(r['net'] or 0)

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

print(f"\n  {'':15s} {'PORTAL':>10s}  {'TALLY':>10s}  {'DIFF':>8s}  STATUS")
print("  " + "-"*55)
for name, portal, tally in [
    ('Revenue',  rev/1e7,     68.00),
    ('Dir Inc',  dir_inc/1e7,  3.93),
    ('COGS',     cogs/1e7,    52.45),
    ('GP',       gp/1e7,      19.49),
    ('Ind Inc',  ind_inc/1e7,  0.16),
    ('Overhead', overhead/1e7, 7.20),
    ('NP',       np_/1e7,     12.44),
]:
    diff = portal - tally
    ok = '✅' if abs(diff)<0.05 else ('🟡' if abs(diff)<0.50 else '❌')
    print(f"  {name:15s} {portal:>10.2f}  {tally:>10.2f}  {diff:>+8.2f}  {ok}")

conn.close()
