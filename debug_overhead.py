"""Run: python debug_overhead.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== 1. Check Indirect Expenses group total row ===")
rows = conn.execute("""
    SELECT ledger_name, tally_group, mis_group, 
           COUNT(*) as cnt, SUM(net) as total
    FROM pl_data
    WHERE company_id=2
      AND ledger_name = 'Indirect Expenses'
    GROUP BY ledger_name, tally_group, mis_group
""").fetchall()
for r in rows:
    print(f"  ledger='{r['ledger_name']}' tg='{r['tally_group']}' mis='{r['mis_group']}' rows={r['cnt']} total={r['total']/1e7:.2f}Cr")

print()
print("=== 2. mis_group='_GROUP_TOTAL_' rows ===")
rows2 = conn.execute("""
    SELECT tally_group, ledger_name, COUNT(*) as cnt
    FROM pl_data WHERE company_id=2 AND mis_group='_GROUP_TOTAL_'
    GROUP BY tally_group, ledger_name
""").fetchall()
for r in rows2:
    print(f"  tg='{r['tally_group']}' ledger='{r['ledger_name']}' rows={r['cnt']}")

print()
print(f"Total _GROUP_TOTAL_ rows: {conn.execute('SELECT COUNT(*) FROM pl_data WHERE mis_group=chr(95)||chr(71)||chr(82)||chr(79)||chr(85)||chr(80)||chr(95)||chr(84)||chr(79)||chr(84)||chr(65)||chr(76)||chr(95)').fetchone()[0]}")

# Try direct
n = conn.execute("SELECT COUNT(*) FROM pl_data WHERE mis_group='_GROUP_TOTAL_'").fetchone()[0]
print(f"Direct count: {n}")

conn.close()
