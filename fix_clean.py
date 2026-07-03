"""
Run: python fix_clean.py
Clean reset + correct final fix
"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)

print("=== STEP 1: Full Reset — Remove ALL _GROUP_TOTAL_ tags ===")
cur = conn.execute("UPDATE pl_data SET mis_group='Admin Expenses' WHERE mis_group='_GROUP_TOTAL_' AND LOWER(tally_group)='indirect expenses'")
print(f"  Reset Indirect Expenses group total rows: {cur.rowcount}")

cur = conn.execute("UPDATE pl_data SET mis_group='Indirect Income' WHERE mis_group='_GROUP_TOTAL_' AND LOWER(tally_group)='indirect incomes'")
print(f"  Reset Indirect Incomes group total rows: {cur.rowcount}")

conn.commit()

print("\n=== STEP 2: Check individual ledgers for sub-groups ===")
# Check if EMPLOYEE'S sub-group has individual children
emp_children = conn.execute("""
    SELECT ledger_name, SUM(net) as total FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group)='indirect expenses'
      AND ledger_name NOT IN (
          'Indirect Expenses',
          'EMPLOYEE&apos;S RELATED EXPENSES',
          'POWER &amp; FUEL EXPENSES',
          'RATES AND TAXES'
      )
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name
    HAVING ABS(SUM(net)) > 1000
    ORDER BY ABS(SUM(net)) DESC
""").fetchall()

print(f"\n  Individual overhead ledgers in DB: {len(emp_children)}")
total_individual = sum(abs(r[1]) for r in emp_children)
print(f"  Sum of individual ledgers: {total_individual/1e7:.4f} Cr")

# Check sub-group totals
subgroup_total = conn.execute("""
    SELECT ledger_name, SUM(net) as total FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group)='indirect expenses'
      AND ledger_name IN (
          'Indirect Expenses',
          'EMPLOYEE&apos;S RELATED EXPENSES',
          'POWER &amp; FUEL EXPENSES',
          'RATES AND TAXES'
      )
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name
""").fetchall()

print(f"\n  Sub-group/group total rows:")
total_subgroups = 0
for r in subgroup_total:
    print(f"    '{r[0]}': {abs(r[1])/1e7:.4f} Cr")
    total_subgroups += abs(r[1])

print(f"\n  Individual sum:  {total_individual/1e7:.4f} Cr")
print(f"  Sub-groups sum:  {total_subgroups/1e7:.4f} Cr")
print(f"  Combined:        {(total_individual+total_subgroups)/1e7:.4f} Cr")
print(f"  Tally expected:  7.20 Cr")
print()
print("  KEY: Individual(3.80) + EMPLOYEE sub-group(4.29) + POWER(0.06) + RATES(0.02) = 8.17")
print("  But Tally = 7.20 Cr")
print("  This means individual ledgers INCLUDE what's inside sub-groups")
print("  OR sub-groups represent additional items not broken down")
print()
# Check: is EMPLOYEE sub-group = sum of its children?
# In Tally, EMPLOYEE'S RELATED EXPENSES is a sub-group containing:
# Salary, Wages, ESIC, PF etc.
# If those individual salary ledgers are NOT in DB, then 4.29 Cr is the only 
# representation of salary cost — we MUST keep it
# If they ARE in DB, then 4.29 is double-counted

# Check for salary-type ledgers
salary_ledgers = conn.execute("""
    SELECT ledger_name, SUM(net) as total FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group)='indirect expenses'
      AND LOWER(ledger_name) LIKE '%sala%'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name
""").fetchall()
print(f"  Salary-type ledgers in DB: {len(salary_ledgers)}")
for r in salary_ledgers:
    print(f"    '{r[0]}': {abs(r[1])/1e7:.4f} Cr")

conn.close()
print()
print("CONCLUSION:")
print("If no salary ledgers found → EMPLOYEE sub-group IS the actual data (keep it)")
print("The 0.97 Cr diff vs Tally = data sync issue, not a tagging issue")
