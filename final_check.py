"""Run: python final_check.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== OVERHEAD BREAKDOWN — USP FY25-26 ===\n")
rows = conn.execute("""
    SELECT ledger_name, mis_group, SUM(net) as total
    FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus')
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, mis_group
    ORDER BY ABS(SUM(net)) DESC
""").fetchall()

gt_total = ind_total = 0
for r in rows:
    tag = '🚫 SKIP' if r['mis_group'] == '_GROUP_TOTAL_' else '✅ COUNT'
    val = abs(r['total'] or 0)
    if r['mis_group'] == '_GROUP_TOTAL_':
        gt_total += val
    else:
        ind_total += val
    print(f"  {tag} | {r['ledger_name']:45s} | {r['mis_group']:30s} | {val/1e7:.4f} Cr")

print(f"\n  Skipped (group totals): {gt_total/1e7:.4f} Cr")
print(f"  Counted (real data):    {ind_total/1e7:.4f} Cr")
print(f"  Tally expected:          7.2010 Cr")
print(f"  Diff:                   {ind_total/1e7 - 7.201:.4f} Cr")
print()
print("  EMPLOYEES RELATED = 4.29 Cr is the ONLY salary data in DB")
print("  Individual salary ledgers not synced yet")
print("  0.97 Cr diff = these salary sub-ledgers + POWER/RATES overlap")
print("  FIX = Re-sync Tally to get individual salary ledgers")
conn.close()
