"""Run: python diagnose_final.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# ── INTELLICHEMIE ─────────────────────────────────────────
print("=== INTELLICHEMIE — Indirect Expenses group total ===")
ie = conn.execute("""
    SELECT ledger_name, tally_group, mis_group,
           SUM(net) as total, COUNT(*) as cnt
    FROM pl_data WHERE company_id=1
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
      AND LOWER(ledger_name)='indirect expenses'
    GROUP BY ledger_name, tally_group, mis_group
""").fetchall()
for r in ie:
    print(f"  tg='{r['tally_group']}' mis='{r['mis_group']}' {r['total']/1e5:.2f}L cnt={r['cnt']}")
    print(f"  → capture condition: tg='indirect expenses' AND ln='indirect expenses' = {str(r['tally_group']).lower()=='indirect expenses' and str(r['ledger_name']).lower()=='indirect expenses'}")

# Check what's happening — maybe tg != 'Indirect Expenses'
all_ie = conn.execute("""
    SELECT DISTINCT tally_group, mis_group, COUNT(*) as cnt, SUM(net) as total
    FROM pl_data WHERE company_id=1
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
      AND ledger_name='Indirect Expenses'
    GROUP BY tally_group, mis_group
""").fetchall()
print(f"\nAll rows with ledger_name='Indirect Expenses' for Intellichemie FY25-26:")
for r in all_ie:
    skip = r['mis_group'] == '_GROUP_TOTAL_'
    print(f"  tg='{r['tally_group']}' mis='{r['mis_group']}' {r['total']/1e5:.2f}L cnt={r['cnt']} {'← SKIP BEFORE CAPTURE!' if skip else ''}")

# ── AVENUECORP COGS ───────────────────────────────────────
print("\n=== AVENUECORP — COGS issue ===")
print("Expected COGS=15.81Cr, Portal=19.87Cr, Diff=4.06Cr")

# Cost of Sales group total FY25-26
cos = conn.execute("""
    SELECT SUM(net) as total FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='cost of sales :'
      AND LOWER(ledger_name)='cost of sales :'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()
print(f"\nCost of Sales group total = {abs(cos['total'] or 0)/1e7:.4f} Cr  (expected 15.81)")

# mis_group of Cost of Sales row
cos_mg = conn.execute("""
    SELECT DISTINCT mis_group FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='cost of sales :'
      AND LOWER(ledger_name)='cost of sales :'
""").fetchall()
print(f"mis_group of Cost of Sales: {[r['mis_group'] for r in cos_mg]}")
print(f"→ If mis_group='_GROUP_TOTAL_', it gets SKIPPED before cos_net capture!")

# Check _calc flow:
# 1. tg='indirect expenses' and ln='indirect expenses' → oh_grp (BEFORE skip) ✅
# 2. tg='salaries and bonus' and ln='salaries and bonus' → oh_sal_grp (BEFORE skip) ✅  
# 3. _is_skip → _GROUP_TOTAL_ ← Cost of Sales has mis='Sales Accounts' not _GROUP_TOTAL_
# 4. tg='cost of sales :' → cos_net ✅
# So COGS should be 15.83 from group total...
# But Avenuecorp portal shows 19.87...
# Let me check what's in _calc for Avenuecorp

# Direct Expenses for Avenuecorp FY25-26
de = conn.execute("""
    SELECT SUM(net) as total FROM pl_data WHERE company_id=3
      AND LOWER(tally_group)='direct expenses'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()
print(f"\nDirect Expenses sum = {abs(de['total'] or 0)/1e7:.4f} Cr")

# Check if Direct Expenses goes into cos_net somehow
cos_all = conn.execute("""
    SELECT tally_group, mis_group, SUM(net) as total FROM pl_data WHERE company_id=3
      AND LOWER(tally_group) IN ('cost of sales :','direct expenses')
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY tally_group, mis_group
    ORDER BY tally_group
""").fetchall()
print(f"\nAll COGS-related rows:")
for r in cos_all:
    print(f"  tg='{r['tally_group']}' mis='{r['mis_group']}' {r['total']/1e7:.4f}Cr")

# Tally: COGS = Opening(3.97) + Purchase(13.47) + DirectExp(0.36) - Closing(1.96) = 15.84
# But portal final_validation shows GP=8.04 meaning COGS=27.91-0+0-8.04... wait
# GP = Rev + DirInc - COGS
# 8.04 = 27.91 + DirInc - COGS
# If DirInc=0: COGS = 27.91 - 8.04 = 19.87 ← confirmed 19.87

# So cos_net = 19.87, not 15.83
# But debug_avenuecorp_cogs.py showed Cost of Sales group total = 15.83!
# Maybe cos_net is picking up something else

conn.close()
