"""
Run: python check_overhead.py
Shows exactly which rows are being counted in Overhead
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== OVERHEAD ROWS — USP FY25-26 (per tally_group+mis_group) ===")
rows = conn.execute("""
    SELECT tally_group, mis_group,
           SUM(net)   as net_sum,
           SUM(abs(net)) as abs_sum,
           COUNT(*)   as row_count,
           COUNT(DISTINCT ledger_name) as ledger_count
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus','salary accounts')
    GROUP BY tally_group, mis_group
    ORDER BY ABS(SUM(net)) DESC
""").fetchall()

total_oh = 0
for r in rows:
    v = abs(r['net_sum'] or 0)
    total_oh += v
    print(f"  {str(r['tally_group']):25s} | {str(r['mis_group']):35s} | {v:>15,.2f} | rows={r['row_count']:4d} | ledgers={r['ledger_count']:3d}")

print(f"\n  Total Overhead = {total_oh:>15,.2f} = {total_oh/1e7:.2f} Cr")
print(f"  Tally Overhead =  72,009,881.92 =  7.20 Cr")
print(f"  Difference     = {total_oh - 72009881.92:>+15,.2f} = {(total_oh-72009881.92)/1e7:+.2f} Cr")

print("\n\n=== TOP 20 INDIVIDUAL OVERHEAD LEDGERS by value ===")
rows2 = conn.execute("""
    SELECT ledger_name, tally_group, mis_group,
           SUM(net) as net_sum, COUNT(*) as months
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus','salary accounts')
    GROUP BY ledger_name, tally_group, mis_group
    ORDER BY ABS(SUM(net)) DESC
    LIMIT 20
""").fetchall()

for r in rows2:
    print(f"  {str(r['ledger_name']):45s} | {str(r['mis_group']):30s} | {abs(r['net_sum']):>15,.2f} | {r['months']} months")

conn.close()
