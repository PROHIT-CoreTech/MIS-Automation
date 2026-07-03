"""
Run: python emergency_fix.py
Restore Sales Accounts group total rows (wrongly tagged as _GROUP_TOTAL_)
"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# Check current state
print("=== CHECKING SALES ACCOUNTS GROUP TOTAL ===")
rows = conn.execute("""
    SELECT ledger_name, tally_group, mis_group, SUM(net) as total, COUNT(*) as cnt
    FROM pl_data
    WHERE ledger_name='Sales Accounts'
    GROUP BY ledger_name, tally_group, mis_group
""").fetchall()
for r in rows:
    print(f"  tg='{r['tally_group']}' mis='{r['mis_group']}' total={r['total']/1e7:.2f}Cr rows={r['cnt']}")

# Fix: restore Sales Accounts group total
cur = conn.execute("""
    UPDATE pl_data SET mis_group='Sales Accounts'
    WHERE ledger_name='Sales Accounts'
      AND tally_group='Sales Accounts'
      AND mis_group='_GROUP_TOTAL_'
""")
print(f"\n  ✅ Restored Sales Accounts group total: {cur.rowcount} rows")

# Also check Direct Incomes group total
print("\n=== CHECKING DIRECT INCOMES GROUP TOTAL ===")
di_rows = conn.execute("""
    SELECT ledger_name, tally_group, mis_group, SUM(net) as total, COUNT(*) as cnt
    FROM pl_data
    WHERE ledger_name='Direct Incomes'
    GROUP BY ledger_name, tally_group, mis_group
""").fetchall()
for r in di_rows:
    print(f"  tg='{r['tally_group']}' mis='{r['mis_group']}' total={r['total']/1e7:.2f}Cr rows={r['cnt']}")

cur2 = conn.execute("""
    UPDATE pl_data SET mis_group='Direct Incomes'
    WHERE ledger_name='Direct Incomes'
      AND tally_group='Direct Incomes'
      AND mis_group='_GROUP_TOTAL_'
""")
print(f"  ✅ Restored Direct Incomes group total: {cur2.rowcount} rows")

conn.commit()

# Verify
print("\n=== VERIFICATION ===")
rev = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2
      AND tally_group='Sales Accounts' AND ledger_name='Sales Accounts'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

di = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2
      AND tally_group='Direct Incomes' AND ledger_name='Direct Incomes'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

cos = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2 AND tally_group='Cost of Sales :'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

oh = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus')
      AND mis_group != '_GROUP_TOTAL_'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

ii = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2 AND LOWER(tally_group)='indirect incomes'
      AND mis_group != '_GROUP_TOTAL_'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

gp  = rev + di - cos
np_ = gp + ii - oh

print(f"\n  {'':15s} {'PORTAL':>10s}  {'TALLY':>10s}  STATUS")
print("  " + "-"*45)
for name, portal, tally in [
    ('Revenue',  rev/1e7, 68.00),
    ('Dir Inc',  di/1e7,   3.93),
    ('COGS',     cos/1e7, 52.45),
    ('GP',       gp/1e7,  19.49),
    ('Ind Inc',  ii/1e7,   0.16),
    ('Overhead', oh/1e7,   7.20),
    ('NP',       np_/1e7, 12.44),
]:
    diff = portal - tally
    ok = '✅' if abs(diff) < 0.05 else ('🟡' if abs(diff) < 0.50 else '❌')
    print(f"  {name:15s} {portal:>10.2f}  {tally:>10.2f}  {ok} {diff:+.2f}")

conn.close()
print("\nDone! Restart portal now.")
