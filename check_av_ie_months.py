"""Run: python check_av_ie_months.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("IE group total per month — Avenuecorp FY25-26:")
rows = conn.execute("""
    SELECT year, month, net
    FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='indirect expenses'
      AND LOWER(ledger_name)='indirect expenses'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    ORDER BY year, month
""").fetchall()

sum_abs = sum_net = 0
for r in rows:
    net = r['net'] or 0
    sum_abs += abs(net)
    sum_net += net
    sign = '+' if net > 0 else '-'
    print(f"  {r['year']}-{r['month']:02d}: net={net/1e7:.4f} abs={abs(net)/1e7:.4f} {sign}")

print(f"\n  SUM(net)    = {sum_net/1e7:.4f} Cr  → abs = {abs(sum_net)/1e7:.4f} Cr")
print(f"  SUM(abs)    = {sum_abs/1e7:.4f} Cr  ← THIS is the problem!")
print(f"  Tally total = 2.41 Cr")
print(f"\n  CORRECT: abs(SUM(net)) = {abs(sum_net)/1e7:.4f} Cr")
print(f"  WRONG:   SUM(abs(net)) = {sum_abs/1e7:.4f} Cr")
print(f"\n  Fix: accumulate net, then take abs at end")
conn.close()
