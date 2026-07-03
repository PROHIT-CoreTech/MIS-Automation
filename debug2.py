import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== OVERHEAD ROWS NOW (USP FY25-26) ===")
rows = conn.execute("""
    SELECT ledger_name, mis_group, SUM(net) as total
    FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus','salary accounts')
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, mis_group
    ORDER BY ABS(SUM(net)) DESC
""").fetchall()

skip_total = count_total = 0
for r in rows:
    skip = r['mis_group'] == '_GROUP_TOTAL_'
    v = abs(r['total'] or 0)
    if skip: skip_total += v
    else: count_total += v
    tag = '🚫' if skip else '✅'
    print(f"  {tag} {r['ledger_name']:45s} {r['mis_group']:25s} {v/1e7:.4f}")

print(f"\n  Skipped: {skip_total/1e7:.4f} Cr")
print(f"  Counted: {count_total/1e7:.4f} Cr  ← Expected 7.20")

print("\n=== DIRECT INCOMES ROWS NOW ===")
di_rows = conn.execute("""
    SELECT ledger_name, mis_group, SUM(net) as total
    FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group) = 'direct incomes'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, mis_group
    ORDER BY ABS(SUM(net)) DESC
""").fetchall()
for r in di_rows:
    print(f"  {r['ledger_name']:45s} {r['mis_group']:25s} {r['total']/1e7:.4f}")

# Also check Freight Outword
print("\n=== FREIGHT OUTWORD CURRENT STATUS ===")
fw = conn.execute("""
    SELECT ledger_name, tally_group, mis_group, SUM(net) as total
    FROM pl_data WHERE ledger_name='Freight Outword'
    GROUP BY ledger_name, tally_group, mis_group
""").fetchall()
for r in fw:
    print(f"  tg='{r['tally_group']}' mis='{r['mis_group']}' total={r['total']/1e7:.4f}")

conn.close()
