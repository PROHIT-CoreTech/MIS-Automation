"""Run: python fix_other_companies.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# ── INTELLICHEMIE (id=1) ───────────────────────────────────
print("="*65)
print("INTELLICHEMIE INDUSTRIES LLP")
print("="*65)

# Check Sales Accounts rows
sa_rows = conn.execute("""
    SELECT ledger_name, mis_group, SUM(net) as total
    FROM pl_data WHERE company_id=1
      AND tally_group='Sales Accounts'
    GROUP BY ledger_name, mis_group
    ORDER BY ABS(SUM(net)) DESC
""").fetchall()

print("\nSales Accounts rows:")
for r in sa_rows:
    print(f"  '{r['ledger_name']}' mis='{r['mis_group']}' val={r['total']/1e7:.4f} Cr")

# Check if 'Sales Accounts' group total row exists
sa_grp = conn.execute("""
    SELECT SUM(net) FROM pl_data
    WHERE company_id=1 AND tally_group='Sales Accounts'
    AND ledger_name='Sales Accounts'
""").fetchone()[0] or 0
print(f"\nSales Accounts group total = {sa_grp/1e7:.4f} Cr")

# Individual ledgers sum
sa_ind = conn.execute("""
    SELECT SUM(net) FROM pl_data
    WHERE company_id=1 AND tally_group='Sales Accounts'
    AND ledger_name != 'Sales Accounts'
""").fetchone()[0] or 0
print(f"Individual ledgers sum     = {sa_ind/1e7:.4f} Cr")

# Check Cost of Sales
cos = conn.execute("""
    SELECT SUM(net) FROM pl_data
    WHERE company_id=1 AND LOWER(tally_group)='cost of sales :'
""").fetchone()[0] or 0
print(f"\nCost of Sales net = {cos/1e7:.4f} Cr")

# Check Direct Expenses
de = conn.execute("""
    SELECT SUM(net) FROM pl_data
    WHERE company_id=1 AND LOWER(tally_group)='direct expenses'
    AND ledger_name != 'Direct Expenses'
""").fetchone()[0] or 0
print(f"Direct Expenses   = {de/1e7:.4f} Cr")

# ── AVENUECORP (id=3) ──────────────────────────────────────
print("\n" + "="*65)
print("AVENUECORP INDIA PRIVATE LIMITED FY 23-24")
print("="*65)

# Check Sales Accounts
av_sa_grp = conn.execute("""
    SELECT SUM(net) FROM pl_data
    WHERE company_id=3 AND tally_group='Sales Accounts'
    AND ledger_name='Sales Accounts'
""").fetchone()[0] or 0

av_sa_ind = conn.execute("""
    SELECT SUM(net) FROM pl_data
    WHERE company_id=3 AND tally_group='Sales Accounts'
    AND ledger_name != 'Sales Accounts'
""").fetchone()[0] or 0

print(f"\nSales Accounts group total = {av_sa_grp/1e7:.4f} Cr")
print(f"Individual ledgers sum     = {av_sa_ind/1e7:.4f} Cr")

# Check Salaries and Bonus double count
sal_grp = conn.execute("""
    SELECT SUM(net) FROM pl_data
    WHERE company_id=3 AND LOWER(tally_group)='salaries and bonus'
    AND mis_group='_GROUP_TOTAL_'
""").fetchone()[0] or 0

sal_ind = conn.execute("""
    SELECT SUM(net) FROM pl_data
    WHERE company_id=3 AND LOWER(tally_group)='salaries and bonus'
    AND mis_group != '_GROUP_TOTAL_'
""").fetchone()[0] or 0

print(f"\nSalaries group total (tagged)   = {sal_grp/1e7:.4f} Cr  ← SKIP")
print(f"Salaries individual rows        = {sal_ind/1e7:.4f} Cr  ← COUNTED")

# Expected P&L for Avenuecorp
av_cos = conn.execute("""
    SELECT SUM(net) FROM pl_data
    WHERE company_id=3 AND LOWER(tally_group)='cost of sales :'
    AND LOWER(ledger_name)='cost of sales :'
""").fetchone()[0] or 0

av_oh = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=3 AND LOWER(tally_group)='indirect expenses'
    AND LOWER(ledger_name)='indirect expenses'
""").fetchone()[0] or 0

av_sal_oh = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=3 AND LOWER(tally_group)='salaries and bonus'
    AND mis_group != '_GROUP_TOTAL_'
""").fetchone()[0] or 0

av_ii = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=3 AND LOWER(tally_group)='indirect incomes'
    AND mis_group != '_GROUP_TOTAL_'
""").fetchone()[0] or 0

rev = av_sa_grp  # use group total
di_grp = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=3 AND LOWER(tally_group)='direct incomes'
    AND LOWER(ledger_name)='direct incomes'
""").fetchone()[0] or 0

gp  = rev + di_grp - abs(av_cos)
oh  = av_oh + av_sal_oh
np_ = gp + av_ii - oh

print(f"\nCalculation:")
print(f"  Revenue (group total) = {rev/1e7:.2f} Cr")
print(f"  Direct Incomes        = {di_grp/1e7:.2f} Cr")
print(f"  COGS                  = {abs(av_cos)/1e7:.2f} Cr")
print(f"  GP                    = {gp/1e7:.2f} Cr")
print(f"  Indirect Incomes      = {av_ii/1e7:.2f} Cr")
print(f"  Overhead (IE+Sal)     = {oh/1e7:.2f} Cr")
print(f"  NP                    = {np_/1e7:.2f} Cr")

conn.close()
