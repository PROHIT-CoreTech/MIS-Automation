"""
Run on your laptop:
cd D:\Freelancing\MIS Portal\MIS_Portal
python check_tally_vs_db.py

This shows EXACT tally_group wise data in DB
so we can see what's tagged vs what should be tagged.
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

cos = conn.execute("SELECT id, tally_name FROM companies").fetchall()

for co in cos:
    cid  = co['id']
    name = co['tally_name']
    print(f"\n{'='*80}")
    print(f"COMPANY: {name}")
    print(f"{'='*80}")

    # Show ALL rows grouped by tally_group with totals
    rows = conn.execute("""
        SELECT 
            COALESCE(tally_group,'NULL')  as tg,
            COALESCE(mis_group,'NULL')    as mg,
            SUM(net)                      as net_sum,
            COUNT(DISTINCT ledger_name)   as ledger_count
        FROM pl_data
        WHERE company_id=?
          AND ((year=2026 AND month BETWEEN 4 AND 6))
        GROUP BY tally_group, mis_group
        ORDER BY tally_group, ABS(SUM(net)) DESC
    """, (cid,)).fetchall()

    if not rows:
        print("  No data for Apr-26 to Jun-26")
        # Try any available period
        any_rows = conn.execute("""
            SELECT DISTINCT year, month FROM pl_data 
            WHERE company_id=? ORDER BY year DESC, month DESC LIMIT 3
        """, (cid,)).fetchall()
        print(f"  Available months: {[(r['year'],r['month']) for r in any_rows]}")
        continue

    print(f"\n  {'Tally Group':35s} {'MIS Group':35s} {'Net Sum':>15s} {'Ledgers':>8s}")
    print("  " + "-"*95)
    for r in rows:
        print(f"  {r['tg']:35s} {r['mg']:35s} {r['net_sum']:>15,.0f} {r['ledger_count']:>8d}")

    # Summary using CORRECT Tally formula
    print(f"\n  {'─'*60}")
    print(f"  FORMULA CHECK (Tally exact):")

    revenue = opening = purchases = direct_exp = closing = 0
    ind_inc = overhead = cost_of_sales_net = 0

    for r in rows:
        tg  = str(r['tg'] or '').lower().strip()
        mg  = str(r['mg'] or '').lower().strip()
        val = abs(r['net_sum'] or 0)

        if tg == 'sales accounts' and mg != 'sales accounts':
            revenue += val
        elif tg == 'cost of sales :':
            cost_of_sales_net = val
        elif tg == 'opening stock':
            opening = val
        elif tg in ('purchase accounts', 'add: purchase accounts'):
            purchases += val
        elif tg == 'direct expenses':
            direct_exp += val
        elif tg in ('less: closing stock', 'closing stock'):
            closing = val
        elif tg in ('direct incomes', 'indirect incomes'):
            ind_inc += val
        elif tg in ('indirect expenses', 'salaries and bonus', 'salary accounts'):
            if mg != 'direct expenses':
                overhead += val

    if cost_of_sales_net:
        cogs = cost_of_sales_net
        mode = "Mode A: Cost of Sales group total"
    else:
        cogs = opening + purchases + direct_exp - closing
        mode = f"Mode B: {opening/1e5:.1f}L Opening + {purchases/1e5:.1f}L Purchases + {direct_exp/1e5:.1f}L DirectExp - {closing/1e5:.1f}L Closing"

    gp  = revenue - cogs
    np_ = gp + ind_inc - overhead

    print(f"  Revenue   : {revenue:>15,.2f}  (tg=Sales Accounts)")
    print(f"  COGS      : {cogs:>15,.2f}  ({mode})")
    print(f"  GP        : {gp:>15,.2f}")
    print(f"  Ind Inc   : {ind_inc:>15,.2f}  (tg=Direct/Indirect Incomes)")
    print(f"  Overhead  : {overhead:>15,.2f}  (tg=Indirect Expenses)")
    print(f"  Net P     : {np_:>15,.2f}")

conn.close()
