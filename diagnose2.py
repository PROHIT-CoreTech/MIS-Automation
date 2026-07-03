"""
Run: python diagnose2.py
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)

# Get exact bytes of the tally_group value for Cost of Sales row
rows = conn.execute("""
    SELECT tally_group, mis_group, net,
           LENGTH(tally_group) as tg_len,
           UNICODE(tally_group) as first_char
    FROM pl_data
    WHERE company_id=2
      AND tally_group LIKE '%Cost%'
      AND year=2025 AND month=4
    LIMIT 5
""").fetchall()

print("=== COST OF SALES ROW — EXACT BYTES ===")
for r in rows:
    tg = r[0]
    print(f"tally_group = '{tg}'")
    print(f"Length      = {r[3]}")
    print(f"First char  = {r[4]} (unicode)")
    print(f"Repr        = {repr(tg)}")
    print(f"Lower+strip = '{tg.lower().strip()}'")
    print(f"Match test  = {tg.lower().strip() == 'cost of sales :'}")
    print()

# Also check all tally_group values with repr
print("\n=== ALL tally_group VALUES (with repr) ===")
all_tg = conn.execute("""
    SELECT DISTINCT tally_group FROM pl_data 
    WHERE company_id=2 ORDER BY tally_group
""").fetchall()
for r in all_tg:
    tg = r[0]
    print(f"  repr: {repr(tg)}")

conn.close()
