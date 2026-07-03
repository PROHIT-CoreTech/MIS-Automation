"""
Run: python check_all_tagging.py
Shows current DB tagging vs what Tally shows
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== USP FY25-26 — ALL LEDGERS WITH CURRENT TAGGING ===\n")

rows = conn.execute("""
    SELECT ledger_name, tally_group, mis_group,
           SUM(net) as total
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, tally_group, mis_group
    ORDER BY tally_group, ledger_name
""").fetchall()

current_tg = ''
for r in rows:
    if r['tally_group'] != current_tg:
        current_tg = r['tally_group']
        print(f"\n  [{current_tg}]")
    print(f"    {str(r['ledger_name']):50s} mis={str(r['mis_group']):35s} val={r['total']/1e7:>8.2f} Cr")

conn.close()
