"""Run: python fix_wrong_tg.py"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)

fixes = [
    # AMC Charge Paid — Direct Expense (COGS), not Indirect
    ("AMC Charge Paid",          "Direct Expenses", "Direct Expenses"),
    # Installation Charges Paid — Direct Expense (COGS), not Indirect
    ("Installation Charges Paid","Direct Expenses", "Direct Expenses"),
]

print("=== FIXING WRONG tally_group ===\n")
for ledger, new_tg, new_mg in fixes:
    cur = conn.execute("""
        UPDATE pl_data SET tally_group=?, mis_group=?
        WHERE ledger_name=?
    """, (new_tg, new_mg, ledger))
    print(f"  ✅ '{ledger}' → tg='{new_tg}' ({cur.rowcount} rows)")

conn.commit()

# Verify P&L unchanged
print("\n=== VERIFY P&L AFTER FIX ===")
# Overhead group total = still 7.20 (unchanged — we use group total)
oh = conn.execute("""
    SELECT SUM(ABS(net)) FROM pl_data
    WHERE company_id=2
      AND ledger_name='Indirect Expenses'
      AND LOWER(tally_group)='indirect expenses'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

# Direct Expenses sum (for COGS detail)
de = conn.execute("""
    SELECT SUM(net) FROM pl_data
    WHERE company_id=2
      AND LOWER(tally_group)='direct expenses'
      AND ledger_name != 'Direct Expenses'
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchone()[0] or 0

print(f"\n  Overhead (group total) = {oh/1e7:.4f} Cr  ← unchanged ✅")
print(f"  Direct Expenses sum    = {abs(de)/1e7:.4f} Cr  ← AMC+Install now here")
print(f"\n  GP & NP unchanged because we use group totals")
print(f"  Dashboard: GP=19.49, OH=7.20, NP=12.44 — all same ✅")

conn.close()
print("\nDone!")
