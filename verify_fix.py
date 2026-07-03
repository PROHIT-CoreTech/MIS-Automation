"""Run: python verify_fix.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)

# Check what overhead calc gives EXCLUDING _GROUP_TOTAL_
result = conn.execute("""
    SELECT 
        SUM(ABS(net)) as total,
        COUNT(*) as rows
    FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus','salary accounts')
      AND mis_group != '_GROUP_TOTAL_'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()
print(f"Overhead excl _GROUP_TOTAL_: {result[0]/1e7:.4f} Cr ({result[1]} rows)")

# Show breakdown
rows = conn.execute("""
    SELECT ledger_name, mis_group, SUM(net) as total
    FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus','salary accounts')
      AND mis_group != '_GROUP_TOTAL_'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, mis_group
    ORDER BY ABS(SUM(net)) DESC
    LIMIT 10
""").fetchall()
print("\nTop 10 overhead ledgers:")
for r in rows:
    print(f"  {str(r[0]):45s} mis={str(r[1]):30s} {abs(r[2])/1e7:.4f}")

# Check if _GROUP_TOTAL_ rows exist
n = conn.execute("SELECT COUNT(*) FROM pl_data WHERE mis_group='_GROUP_TOTAL_'").fetchone()[0]
print(f"\n_GROUP_TOTAL_ rows in DB: {n}")

# Check Indirect Expenses row specifically
ie = conn.execute("""
    SELECT ledger_name, tally_group, mis_group, SUM(net) as total
    FROM pl_data WHERE ledger_name='Indirect Expenses'
    GROUP BY ledger_name, tally_group, mis_group
""").fetchall()
print("\nAll 'Indirect Expenses' ledger rows:")
for r in ie:
    print(f"  tg='{r[1]}' mis='{r[2]}' total={r[3]/1e7:.4f} Cr")

conn.close()
