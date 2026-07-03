"""
Run: python fix_direct_incomes.py
Fix Direct Incomes tagging:
- Group total row (ledger_name='Direct Incomes') → mis_group='Direct Incomes' (for dir_inc_total)
- Individual ledgers → mis_group='Direct Income Item' (goes to dir_inc_items)
"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== BEFORE FIX — Direct Incomes rows ===")
rows = conn.execute("""
    SELECT ledger_name, mis_group, SUM(net) as total
    FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group)='direct incomes'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, mis_group
    ORDER BY ABS(SUM(net)) DESC
""").fetchall()
for r in rows:
    print(f"  ln='{r['ledger_name']}' mis='{r['mis_group']}' {r['total']/1e7:.4f} Cr")

# Fix: ALL individual ledgers (not the group total) get a distinct mis_group
# So _calc can distinguish: group total vs individual items
cur = conn.execute("""
    UPDATE pl_data
    SET mis_group = 'Direct Income Item'
    WHERE LOWER(tally_group) = 'direct incomes'
      AND ledger_name != 'Direct Incomes'
""")
print(f"\n  ✅ Individual ledgers → 'Direct Income Item': {cur.rowcount} rows")

conn.commit()

print("\n=== AFTER FIX — Direct Incomes rows ===")
rows2 = conn.execute("""
    SELECT ledger_name, mis_group, SUM(net) as total
    FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group)='direct incomes'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, mis_group
    ORDER BY ABS(SUM(net)) DESC
""").fetchall()
for r in rows2:
    print(f"  ln='{r['ledger_name']}' mis='{r['mis_group']}' {r['total']/1e7:.4f} Cr")

# Verify P&L
print("\n=== FINAL P&L VERIFICATION ===")
rows3 = conn.execute("""
    SELECT ledger_name, mis_group, tally_group, net
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchall()

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

rev_total=dir_inc_total=dir_inc_items=cos_net=ind_inc=overhead=0
cos_net_found=False

for r in rows3:
    tg  = str(r['tally_group'] or '').lower().strip()
    mg  = str(r['mis_group']   or '').lower().strip()
    ln  = str(r['ledger_name'] or '').lower().strip()
    val = abs(r['net'] or 0)

    if tg in HEADERS or mg in HEADERS: continue
    if mg == '_group_total_': continue
    if ln == tg and tg not in ('sales accounts','cost of sales :','direct incomes'):
        continue

    if tg == 'sales accounts':
        if mg == 'sales accounts': rev_total += val
        continue
    if tg == 'direct incomes':
        if mg == 'direct incomes': dir_inc_total += val   # group total only
        else: dir_inc_items += val                         # individual items
        continue
    if tg == 'cost of sales :':
        cos_net += val; cos_net_found=True; continue
    if tg == 'indirect incomes':
        ind_inc += val; continue
    if tg in ('indirect expenses','salaries and bonus','salary accounts'):
        overhead += val; continue

dir_inc = dir_inc_total if dir_inc_total else dir_inc_items
cogs = cos_net if cos_net_found else 0
gp   = rev_total + dir_inc - cogs
np_  = gp + ind_inc - overhead

print(f"\n  {'':15s} {'PORTAL':>10s}  {'TALLY':>10s}  {'DIFF':>8s}  STATUS")
print("  " + "-"*55)
for name, portal, tally in [
    ('Revenue',   rev_total/1e7, 68.00),
    ('Dir Inc',   dir_inc/1e7,    3.93),
    ('COGS',      cogs/1e7,      52.45),
    ('GP',        gp/1e7,        19.49),
    ('Ind Inc',   ind_inc/1e7,    0.16),
    ('Overhead',  overhead/1e7,   7.20),
    ('NP',        np_/1e7,       12.44),
]:
    diff = portal - tally
    ok = '✅' if abs(diff)<0.05 else ('🟡' if abs(diff)<0.70 else '❌')
    print(f"  {name:15s} {portal:>10.2f}  {tally:>10.2f}  {diff:>+8.2f}  {ok}")

conn.close()
print("\nDone! Restart portal to verify.")
