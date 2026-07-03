"""
Run: python fix_tagging.py
Fixes all tagging issues found by comparing Tally screenshots vs DB
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)

fixes = [
    # ── ISSUE 1: Turnover Discount ──────────────────────────
    # Tally: Direct Incomes group → should be in Trading A/c credit
    # DB: tally_group='Indirect Incomes' → WRONG
    # Fix: move to Direct Incomes
    {
        'desc': 'Turnover Discount → Direct Incomes (Trading A/c credit)',
        'ledger': 'Turnover Discount',
        'new_tally_group': 'Direct Incomes',
        'new_mis_group': 'Direct Incomes',
    },

    # ── ISSUE 2: Packing Charges ────────────────────────────
    # Tally: Direct Incomes group
    # DB: tally_group='Indirect Incomes', mis='Other Income' → WRONG
    {
        'desc': 'Packing Charges → Direct Incomes',
        'ledger': 'Packing Charges',
        'new_tally_group': 'Direct Incomes',
        'new_mis_group': 'Direct Incomes',
    },

    # ── ISSUE 3: Service Charges ────────────────────────────
    # Tally: Direct Incomes group
    # DB: tally_group='Indirect Incomes', mis='Other Income' → WRONG
    {
        'desc': 'Service Charges → Direct Incomes',
        'ledger': 'Service Charges',
        'new_tally_group': 'Direct Incomes',
        'new_mis_group': 'Direct Incomes',
    },

    # ── ISSUE 4: Factory Maintenance ───────────────────────
    # Tally: Indirect Expenses group
    # DB: tally_group='Direct Expenses' → WRONG
    {
        'desc': 'Factory Maintenance → Indirect Expenses',
        'ledger': 'Factory Maintenance',
        'new_tally_group': 'Indirect Expenses',
        'new_mis_group': 'Admin Expenses',
    },

    # ── ISSUE 5: Huzefa -Imprest ────────────────────────────
    # Tally: Indirect Expenses group
    # DB: tally_group='Cash-in-hand' → WRONG
    {
        'desc': 'Huzefa -Imprest → Indirect Expenses',
        'ledger': 'Huzefa -Imprest',
        'new_tally_group': 'Indirect Expenses',
        'new_mis_group': 'Admin Expenses',
    },

    # ── ISSUE 6: Petrol Charges ─────────────────────────────
    # Tally: Indirect Expenses (correct group)
    # DB: mis='Admin Expenses' → should be Petrol and Travelling
    {
        'desc': 'Petrol Charges mis_group → Petrol and Travelling Expenses',
        'ledger': 'Petrol Charges',
        'new_tally_group': 'Indirect Expenses',
        'new_mis_group': 'Petrol and Travelling Expenses',
    },

    # ── ISSUE 7: Customs Duty ───────────────────────────────
    # Tally: Direct Expenses (COGS)
    # DB: mis='Custom Duty' → rename to match standard
    {
        'desc': 'Customs Duty mis_group → Direct Expenses (standardize)',
        'ledger': 'Customs Duty',
        'new_tally_group': 'Direct Expenses',
        'new_mis_group': 'Direct Expenses',
    },

    # ── ISSUE 8: Job Work Charges Paid ──────────────────────
    # DB: mis='Job Work Charges Paid' → should be Direct Expenses
    {
        'desc': 'Job Work Charges Paid mis_group → Direct Expenses',
        'ledger': 'Job Work Charges Paid',
        'new_tally_group': 'Direct Expenses',
        'new_mis_group': 'Direct Expenses',
    },

    # ── ISSUE 9: Job Work Charges Received ──────────────────
    # DB: mis='Job Work Charges Received' → should be Direct Incomes
    {
        'desc': 'Job Work Charges Received mis_group → Direct Incomes',
        'ledger': 'Job Work Charges Received',
        'new_tally_group': 'Direct Incomes',
        'new_mis_group': 'Direct Incomes',
    },

    # ── ISSUE 10: Bank Charges ──────────────────────────────
    # DB: mis='Finance Cost' → should be Admin Expenses (Tally: Indirect Expenses)
    {
        'desc': 'Bank Charges mis_group → Finance Cost (keep - correct)',
        'ledger': 'Bank Charges',
        'new_tally_group': 'Indirect Expenses',
        'new_mis_group': 'Finance Cost',
    },
]

print(f"{'='*70}")
print(f"APPLYING TAGGING FIXES")
print(f"{'='*70}\n")

total = 0
for fix in fixes:
    cur = conn.execute("""
        UPDATE pl_data
        SET tally_group=?, mis_group=?
        WHERE ledger_name=?
    """, (fix['new_tally_group'], fix['new_mis_group'], fix['ledger']))
    n = cur.rowcount
    total += n
    status = f"✅ {n} rows" if n > 0 else "⚠️  0 rows (not found)"
    print(f"  {status}  |  {fix['desc']}")

conn.commit()
print(f"\nTotal rows updated: {total}")

# ── VERIFY FINAL STATE ─────────────────────────────────────
print(f"\n{'='*70}")
print("VERIFICATION — KEY GROUPS AFTER FIX")
print(f"{'='*70}")

for grp in ['Direct Incomes', 'Direct Expenses', 'Indirect Incomes', 'Indirect Expenses']:
    rows = conn.execute("""
        SELECT ledger_name, tally_group, mis_group, SUM(net) as total
        FROM pl_data
        WHERE company_id=2
          AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
          AND tally_group=?
          AND ledger_name != tally_group
        GROUP BY ledger_name, mis_group
        ORDER BY ledger_name
    """, (grp,)).fetchall()

    print(f"\n  [{grp}]  ({len(rows)} ledgers)")
    for r in rows:
        print(f"    {str(r['ledger_name']):50s} → {str(r['mis_group']):35s} {r['total']/1e7:>7.2f} Cr")

conn.close()
print("\nDone! Restart portal to see changes.")
