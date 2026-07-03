"""
Run: python fix_db2.py
Fix all 124 remaining ledgers:
tally_group='Indirect Expenses' + mis_group='Direct Expenses'
→ These ARE overhead — update mis_group to 'Admin Expenses'
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)

# Proper MIS group mapping for known ledger patterns
EXPENSE_MAP = {
    # Employee related
    'salary':           'Employee Benefits',
    'salaries':         'Employee Benefits',
    'wages':            'Employee Benefits',
    'esic':             'Employee Benefits',
    'epfo':             'Employee Benefits',
    'pf expense':       'Employee Benefits',
    'pf ':              'Employee Benefits',
    'bonus':            'Employee Benefits',
    'gratuity':         'Employee Benefits',
    'hr expense':       'Employee Benefits',
    'recruitment':      'Employee Benefits',
    'training':         'Employee Benefits',
    'traning':          'Employee Benefits',
    'employee':         'Employee Benefits',
    'food expense':     'Employee Benefits',
    'uniform':          'Employee Benefits',
    'workmen':          'Employee Benefits',
    'manpower':         'Employee Benefits',
    'performance bonus':'Employee Benefits',
    # Finance / Interest
    'interest':         'Finance Cost',
    'bank interest':    'Finance Cost',
    'loan processing':  'Finance Cost',
    'late fees on gst': 'Finance Cost',
    'late filing fees': 'Finance Cost',
    'tds late':         'Finance Cost',
    'tds appeal':       'Finance Cost',
    # Petrol / Travel
    'petrol':           'Petrol and Travelling Expenses',
    'diesel':           'Petrol and Travelling Expenses',
    'fuel':             'Petrol and Travelling Expenses',
    'toll':             'Petrol and Travelling Expenses',
    'travelling':       'Petrol and Travelling Expenses',
    'travel':           'Petrol and Travelling Expenses',
    'conv &':           'Petrol and Travelling Expenses',
    'car expense':      'Petrol and Travelling Expenses',
    'car hiring':       'Petrol and Travelling Expenses',
    'vehicle':          'Petrol and Travelling Expenses',
    'vehical':          'Petrol and Travelling Expenses',
    'hotel':            'Petrol and Travelling Expenses',
    # Admin (everything else)
}

def get_mis(ledger_name):
    """Map ledger to correct MIS group based on name"""
    l = ledger_name.lower()
    for keyword, mis in EXPENSE_MAP.items():
        if keyword in l:
            return mis
    return 'Admin Expenses'  # default for all other overhead

# Get all remaining problem rows
rows = conn.execute("""
    SELECT DISTINCT ledger_name FROM pl_data
    WHERE LOWER(tally_group) = 'indirect expenses'
      AND LOWER(mis_group)   = 'direct expenses'
    ORDER BY ledger_name
""").fetchall()

print(f"Fixing {len(rows)} ledger types...")
total_updated = 0

for r in rows:
    ledger  = r[0]
    new_mis = get_mis(ledger)
    cur = conn.execute("""
        UPDATE pl_data SET mis_group=?
        WHERE ledger_name=?
          AND LOWER(tally_group)='indirect expenses'
          AND LOWER(mis_group)='direct expenses'
    """, (new_mis, ledger))
    total_updated += cur.rowcount
    print(f"  ✅ '{ledger}' → '{new_mis}' ({cur.rowcount} rows)")

conn.commit()
print(f"\nTotal rows updated: {total_updated}")

# ── VERIFY FINAL RESULT ────────────────────────────────────
print("\n" + "="*60)
print("FINAL VERIFICATION — USP FY25-26")
print("="*60)

rows = conn.execute("""
    SELECT tally_group, mis_group, SUM(net) as s
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY tally_group, mis_group
    ORDER BY tally_group, ABS(SUM(net)) DESC
""").fetchall()

rev = dir_g = dir_i = cos = oh = ind_inc = 0
for r in rows:
    tg  = str(r[0] or '').lower().strip()
    mg  = str(r[1] or '').lower().strip()
    v   = abs(r[2] or 0)

    if   tg == 'sales accounts' and mg == 'sales accounts': rev    += v
    elif tg == 'direct incomes' and mg == 'direct incomes': dir_g  += v
    elif tg == 'direct incomes':                            dir_i  += v
    elif tg == 'cost of sales :':                           cos    += v
    elif tg == 'indirect incomes':                          ind_inc+= v
    elif tg in ('indirect expenses','salaries and bonus','salary accounts'):
        oh += v  # ALL included now — no exclusions

dir_inc = max(dir_g, dir_i)
gp  = rev + dir_inc - cos
np_ = gp + ind_inc - oh

print(f"\n  {'':20s} {'Portal':>12s}  {'Tally':>12s}  {'Diff':>12s}")
print("  " + "-"*55)
print(f"  {'Revenue':20s} {rev/1e7:>11.2f}  {68.00:>11.2f}  {(rev/1e7-68.00):>+11.2f}")
print(f"  {'Gross Profit':20s} {gp/1e7:>11.2f}  {19.49:>11.2f}  {(gp/1e7-19.49):>+11.2f}")
print(f"  {'Overhead':20s} {oh/1e7:>11.2f}  {7.20:>11.2f}  {(oh/1e7-7.20):>+11.2f}")
print(f"  {'Net Profit':20s} {np_/1e7:>11.2f}  {12.44:>11.2f}  {(np_/1e7-12.44):>+11.2f}")

conn.close()
print("\nDone! Run portal now — values should match Tally.")
