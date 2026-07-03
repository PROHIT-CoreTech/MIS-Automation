"""
Run: python fix_employee_subgroup.py
Tags sub-group total rows that are not real ledgers
"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# These are sub-group totals stored as if they were ledgers
# They appear in Tally XML as group headers, not individual ledgers
SUB_GROUP_TOTALS = [
    "EMPLOYEE'S RELATED EXPENSES",   # = Salaries + ESIC + PF group total
    "EMPLOYEE&apos;S RELATED EXPENSES",  # HTML encoded version
    "POWER & FUEL EXPENSES",         # sub-group total
    "POWER &amp; FUEL EXPENSES",     # HTML encoded
    "RATES AND TAXES",               # sub-group total
]

print("=== BEFORE FIX ===")
before = conn.execute("""
    SELECT SUM(ABS(net)) as total FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus','salary accounts')
      AND mis_group != '_GROUP_TOTAL_'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()
print(f"Overhead before: {before[0]/1e7:.4f} Cr")

# Tag sub-group totals
total_tagged = 0
for ledger in SUB_GROUP_TOTALS:
    cur = conn.execute("""
        UPDATE pl_data SET mis_group='_GROUP_TOTAL_'
        WHERE ledger_name=?
          AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus')
    """, (ledger,))
    if cur.rowcount > 0:
        print(f"  ✅ Tagged '{ledger}' → {cur.rowcount} rows")
        total_tagged += cur.rowcount

# Also tag any row where ledger_name is a known Tally group name
# (these are sub-group totals that slipped through)
known_tally_groups = [
    'Direct Expenses', 'Purchase Accounts', 'Sales Accounts',
    'Direct Incomes', 'Indirect Expenses', 'Indirect Incomes',
    'Salaries and Bonus', 'Opening Stock', 'Closing Stock'
]
for grp in known_tally_groups:
    cur = conn.execute("""
        UPDATE pl_data SET mis_group='_GROUP_TOTAL_'
        WHERE ledger_name=?
          AND mis_group != '_GROUP_TOTAL_'
    """, (grp,))
    if cur.rowcount > 0:
        print(f"  ✅ Tagged sub-group '{grp}' → {cur.rowcount} rows")
        total_tagged += cur.rowcount

conn.commit()
print(f"\nTotal newly tagged: {total_tagged} rows")

print("\n=== AFTER FIX ===")
after = conn.execute("""
    SELECT SUM(ABS(net)) as total FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus','salary accounts')
      AND mis_group != '_GROUP_TOTAL_'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()
print(f"Overhead after:  {after[0]/1e7:.4f} Cr  (expected 7.20 Cr)")

# Full P&L check
rows = conn.execute("""
    SELECT tally_group, mis_group, ledger_name, SUM(net) as s
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
      AND mis_group != '_GROUP_TOTAL_'
    GROUP BY tally_group, mis_group, ledger_name
""").fetchall()

rev = dir_g = dir_i = cos = oh = ind_inc = 0
for r in rows:
    tg = str(r[1] or '').lower().strip()  # mis_group not tally_group
    tg_raw = str(r[0] or '').lower().strip()
    ln = str(r[2] or '').lower().strip()
    v  = abs(r[3] or 0)
    if ln == tg_raw: continue  # skip remaining group totals
    if   tg_raw == 'sales accounts' and r[1] == 'Sales Accounts': rev    += v
    elif tg_raw == 'sales accounts':                               rev    += v
    elif tg_raw == 'direct incomes' and r[1] == 'Direct Incomes': dir_g  += v
    elif tg_raw == 'direct incomes':                               dir_i  += v
    elif tg_raw == 'cost of sales :':                              cos    += v
    elif tg_raw == 'indirect incomes':                             ind_inc+= v
    elif tg_raw in ('indirect expenses','salaries and bonus'):     oh     += v

print(f"\nRevenue  : {rev/1e7:.2f} Cr  (expected 68.00)")
print(f"Overhead : {oh/1e7:.2f} Cr  (expected  7.20)")
print(f"Ind Inc  : {ind_inc/1e7:.2f} Cr  (expected  0.16)")
conn.close()
