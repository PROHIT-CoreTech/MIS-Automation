"""
Run: python check_cogs.py
Shows exactly what COGS data is in DB for USP
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== COGS RELATED ROWS IN DB (USP FY25-26) ===\n")

rows = conn.execute("""
    SELECT tally_group, ledger_name, mis_group,
           SUM(net) as total, COUNT(*) as months
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
      AND LOWER(tally_group) IN (
          'cost of sales :','opening stock','less: closing stock',
          'closing stock','purchase accounts','add: purchase accounts',
          'direct expenses'
      )
    GROUP BY tally_group, ledger_name, mis_group
    ORDER BY tally_group, ABS(SUM(net)) DESC
""").fetchall()

for r in rows:
    print(f"  tg: {r['tally_group']:25s} | ledger: {r['ledger_name']:35s} | {r['total']:>15,.2f}")

conn.close()
