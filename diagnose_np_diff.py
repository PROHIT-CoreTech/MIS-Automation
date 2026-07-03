"""Run: python diagnose_np_diff.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("="*65)
print("NET PROFIT DIFFERENCE ANALYSIS")
print("Portal = 11.78 Cr | Tally = 12.44 Cr | Diff = 0.66 Cr")
print("="*65)

# Step 1: Get exact overhead breakdown
print("\n1. OVERHEAD BREAKDOWN (what's counted vs skipped)")
oh_rows = conn.execute("""
    SELECT ledger_name, mis_group, SUM(net) as total
    FROM pl_data WHERE company_id=2
      AND LOWER(tally_group) IN ('indirect expenses','salaries and bonus')
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, mis_group
    ORDER BY ABS(SUM(net)) DESC
""").fetchall()

counted = skipped = 0
print(f"\n  {'Status':6s} {'Ledger':45s} {'Value':>10s}")
print("  " + "-"*65)
for r in oh_rows:
    v = abs(r['total'] or 0)
    skip = r['mis_group'] == '_GROUP_TOTAL_'
    if skip: skipped += v
    else: counted += v
    tag = 'SKIP' if skip else 'ADD '
    print(f"  {tag}   {str(r['ledger_name']):45s} {v/1e7:>10.4f} Cr")

print(f"\n  Counted (portal overhead) = {counted/1e7:.4f} Cr")
print(f"  Tally overhead            = 7.2010 Cr")
print(f"  Diff                      = {counted/1e7 - 7.201:+.4f} Cr")

# Step 2: Identify exact extra rows
print("\n2. EXACT EXTRA ROWS IN OVERHEAD vs TALLY")
print("   (rows that exist in portal but not as individual items in Tally)")
print()
print("   EMPLOYEE'S RELATED EXPENSES = sub-group total")
print("   Individual salary ledgers (Salary, ESIC, PF) = NOT in DB")
print("   This sub-group IS the only salary data = must keep")
print()

# Step 3: What makes up the 0.67 Cr diff
emp = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data WHERE company_id=2
      AND ledger_name="EMPLOYEE&apos;S RELATED EXPENSES"
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

other_counted = counted - emp
tally_non_emp = 7.2010e7 - emp  # what Tally shows minus employee portion

print(f"   EMPLOYEE'S sub-group     = {emp/1e7:.4f} Cr")
print(f"   Other individual ledgers = {other_counted/1e7:.4f} Cr")
print(f"   Total portal overhead    = {counted/1e7:.4f} Cr")
print()
print(f"   Tally total overhead     = 7.2010 Cr")
print(f"   Diff                     = {counted/1e7 - 7.2010:.4f} Cr")
print()
print("3. ROOT CAUSE")
print()
print("   Tally P&L shows Indirect Expenses = 7.20 Cr")
print("   This 7.20 Cr = EMPLOYEE'S sub-group + all individual ledgers")
print("   EMPLOYEE'S sub-group total = already includes salary children")
print("   But DB also has those same children as individual rows? NO")
print()
print("   Individual ledgers sum = ", other_counted/1e7, "Cr")
print("   EMPLOYEE'S sub-group   = ", emp/1e7, "Cr")
print("   If Tally = 7.20, and EMPLOYEE = 4.29, then others = 2.91 Cr")
print(f"   Portal others = {other_counted/1e7:.4f} Cr")
print(f"   Extra in portal = {other_counted/1e7 - 2.91:.4f} Cr")

conn.close()
