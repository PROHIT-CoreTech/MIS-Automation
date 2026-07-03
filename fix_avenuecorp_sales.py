"""Run: python fix_avenuecorp_sales.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== FIX: Sales Accounts individual ledgers mis_group ===\n")

# Check ALL companies — same issue may exist
companies = conn.execute("SELECT id, tally_name FROM companies").fetchall()

for co in companies:
    cid = co['id']
    name = co['tally_name']

    # Individual ledgers (not group total row) with mis_group='Sales Accounts'
    ind = conn.execute("""
        SELECT ledger_name, mis_group, SUM(net) as total
        FROM pl_data WHERE company_id=?
          AND tally_group='Sales Accounts'
          AND ledger_name != 'Sales Accounts'
          AND mis_group='Sales Accounts'
        GROUP BY ledger_name, mis_group
        ORDER BY ABS(SUM(net)) DESC
    """, (cid,)).fetchall()

    if not ind:
        print(f"  {name}: No fix needed ✅")
        continue

    print(f"  {name}: {len(ind)} individual ledgers with mis_group='Sales Accounts'")
    for r in ind:
        print(f"    '{r['ledger_name']}' = {r['total']/1e7:.4f} Cr")

    # Fix: change to 'Sales Ledger' so _calc skips them
    cur = conn.execute("""
        UPDATE pl_data SET mis_group='Sales Ledger'
        WHERE company_id=?
          AND tally_group='Sales Accounts'
          AND ledger_name != 'Sales Accounts'
          AND mis_group='Sales Accounts'
    """, (cid,))
    print(f"    → Fixed {cur.rowcount} rows: mis_group='Sales Ledger'\n")

conn.commit()

# Verify Avenuecorp FY25-26
print("=== VERIFICATION — Avenuecorp FY25-26 ===\n")

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

rows = conn.execute("""
    SELECT ledger_name, mis_group, tally_group, net
    FROM pl_data WHERE company_id=3
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchall()

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
        oh_sal += v
    elif tg in ('indirect expenses','salary accounts'):
        oh_items += v

dir_inc  = dir_g if dir_g else dir_i
overhead = (oh_grp if oh_found else oh_items) + oh_sal
cogs     = cos if cos_found else 0
gp       = rev + dir_inc - cogs
np_      = gp + ind_inc - overhead

print(f"  {'':12s} {'PORTAL':>10s}  {'TALLY':>10s}  {'DIFF':>8s}  STATUS")
print("  " + "-"*50)
for name2, portal, tally in [
    ('Revenue',  rev/1e7,      27.9083),
    ('COGS',     cogs/1e7,     15.8144),
    ('GP',       gp/1e7,       12.0738),
    ('Ind Inc',  ind_inc/1e7,   0.00),
    ('Overhead', overhead/1e7,  6.1536),
    ('NP',       np_/1e7,       5.9309),
]:
    diff = portal - tally
    ok = '✅' if abs(diff)<0.05 else ('🟡' if abs(diff)<1.0 else '❌')
    print(f"  {name2:12s} {portal:>10.4f}  {tally:>10.4f}  {diff:>+8.4f}  {ok}")

# Also check USP not affected
print("\n=== USP FY25-26 still correct? ===")
usp = conn.execute("""
    SELECT ledger_name, mis_group FROM pl_data
    WHERE company_id=2 AND tally_group='Sales Accounts'
    GROUP BY ledger_name, mis_group
""").fetchall()
for r in usp:
    print(f"  '{r['ledger_name']}' mis='{r['mis_group']}'")

conn.close()
