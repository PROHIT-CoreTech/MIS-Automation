"""Run: python debug_av_oh.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=== Avenuecorp FY25-26 — IE group total ===")
ie = conn.execute("""
    SELECT ledger_name, tally_group, mis_group,
           SUM(net) as total, COUNT(*) as cnt
    FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='indirect expenses'
      AND LOWER(ledger_name)='indirect expenses'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, tally_group, mis_group
""").fetchall()
for r in ie:
    print(f"  tg='{r['tally_group']}' mis='{r['mis_group']}' {r['total']/1e7:.4f}Cr cnt={r['cnt']}")
    print(f"  Tally = 2.41 Cr, Portal = {abs(r['total'])/1e7:.4f} Cr, Diff = {abs(r['total'])/1e7 - 2.4088:.4f}")

print("\n=== Salaries group total ===")
sal = conn.execute("""
    SELECT ledger_name, tally_group, mis_group,
           SUM(net) as total, COUNT(*) as cnt
    FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='salaries and bonus'
      AND LOWER(ledger_name)='salaries and bonus'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, tally_group, mis_group
""").fetchall()
for r in sal:
    print(f"  tg='{r['tally_group']}' mis='{r['mis_group']}' {r['total']/1e7:.4f}Cr cnt={r['cnt']}")
    print(f"  Tally = 3.74 Cr, Portal = {abs(r['total'])/1e7:.4f} Cr, Diff = {abs(r['total'])/1e7 - 3.7447:.4f}")

# Check if 0.10 Cr diff matches any specific ledger
print("\n=== IE individual ledgers (top items) ===")
ie_ind = conn.execute("""
    SELECT ledger_name, SUM(net) as total
    FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='indirect expenses'
      AND LOWER(ledger_name)!='indirect expenses'
      AND mis_group!='_GROUP_TOTAL_'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name
    ORDER BY ABS(SUM(net)) DESC LIMIT 10
""").fetchall()
ind_total = 0
for r in ie_ind:
    ind_total += abs(r['total'] or 0)
    print(f"  '{r['ledger_name']}' = {r['total']/1e7:.4f} Cr")

full_ind = conn.execute("""
    SELECT SUM(ABS(net)) as total FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='indirect expenses'
      AND LOWER(ledger_name)!='indirect expenses'
      AND mis_group!='_GROUP_TOTAL_'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()['total'] or 0
print(f"\n  IE individual sum = {full_ind/1e7:.4f} Cr")
print(f"  IE group total    = 2.4088 Cr (Tally)")
print(f"  Diff              = {full_ind/1e7 - 2.4088:.4f} Cr ← extra in individual sum")
print(f"\nNote: 0.10 Cr diff in overhead = IE group total portal({abs(conn.execute('SELECT SUM(net) FROM pl_data WHERE company_id=3 AND LOWER(tally_group)=chr(105)||chr(110)||chr(100)||chr(105)||chr(114)||chr(101)||chr(99)||chr(116)||chr(32)||chr(101)||chr(120)||chr(112)||chr(101)||chr(110)||chr(115)||chr(101)||chr(115) AND LOWER(ledger_name)=LOWER(tally_group) AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))').fetchone()[0] or 0)/1e7:.4f}) vs Tally(2.41)")
conn.close()
