"""
Run: python fix_db.py
Fixes mis_group tagging in DB based on Masters.xlsx
So portal calculations match Tally exactly.
"""
import sqlite3, os, openpyxl

DB       = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
MASTERS  = os.path.join(os.path.dirname(__file__), 'config', 'masters', 'Masters.xlsx')

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# ── Load Masters.xlsx ──────────────────────────────────────
# Col A = Ledger Name, Col B = Tally Group, Col C = MIS Group
masters = {}  # ledger_name → (tally_group, mis_group)
if os.path.exists(MASTERS):
    wb = openpyxl.load_workbook(MASTERS, data_only=True)
    ws = wb.active
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]: continue
        ledger = str(row[0] or '').strip()
        tg     = str(row[1] or '').strip()
        mg     = str(row[2] or '').strip() if len(row) > 2 else tg
        if ledger and tg:
            masters[ledger] = (tg, mg)
    print(f"Masters.xlsx loaded: {len(masters)} ledgers")
else:
    print(f"WARNING: Masters.xlsx not found at {MASTERS}")

# ── Show current problem rows ──────────────────────────────
print("\n=== CURRENT PROBLEM ROWS (mis_group='Direct Expenses' under Indirect Expenses) ===")
problem = conn.execute("""
    SELECT DISTINCT ledger_name, tally_group, mis_group
    FROM pl_data
    WHERE LOWER(tally_group) = 'indirect expenses'
      AND LOWER(mis_group)   = 'direct expenses'
    ORDER BY ledger_name
""").fetchall()

print(f"\n{'Ledger Name':45s} {'Tally Group':25s} {'Current MIS':25s} {'Should Be':25s}")
print("-"*122)
fixes = []
for r in problem:
    ledger = r['ledger_name']
    should = masters.get(ledger, (None, None))[1] or '❌ NOT IN MASTERS'
    print(f"  {ledger:43s} {r['tally_group']:25s} {r['mis_group']:25s} {should:25s}")
    if masters.get(ledger):
        fixes.append((masters[ledger][0], masters[ledger][1], ledger))

print(f"\nTotal: {len(problem)} ledger rows")
print(f"Fixable (in Masters): {len(fixes)}")
print(f"NOT in Masters: {len(problem) - len(fixes)}")

# ── Apply fixes ────────────────────────────────────────────
if fixes:
    print(f"\n=== APPLYING FIXES ===")
    updated = 0
    for tg, mg, ledger in fixes:
        cur = conn.execute("""
            UPDATE pl_data SET mis_group=? WHERE ledger_name=? 
            AND LOWER(tally_group)='indirect expenses'
            AND LOWER(mis_group)='direct expenses'
        """, (mg, ledger))
        if cur.rowcount:
            print(f"  ✅ Fixed: '{ledger}' → mis_group='{mg}' ({cur.rowcount} rows)")
            updated += cur.rowcount
    conn.commit()
    print(f"\nTotal rows updated: {updated}")

# ── Show remaining NOT in Masters ─────────────────────────
remaining = conn.execute("""
    SELECT DISTINCT ledger_name, tally_group, mis_group
    FROM pl_data
    WHERE LOWER(tally_group) = 'indirect expenses'
      AND LOWER(mis_group)   = 'direct expenses'
    ORDER BY ledger_name
""").fetchall()

if remaining:
    print(f"\n=== STILL NEED MASTERS ENTRY ({len(remaining)} ledgers) ===")
    for r in remaining:
        print(f"  ❌ '{r['ledger_name']}' — Add to Masters.xlsx as Indirect Expenses → Employee Benefits")

# ── Verify result ──────────────────────────────────────────
print("\n=== VERIFICATION — USP FY25-26 After Fix ===")
rows = conn.execute("""
    SELECT tally_group, mis_group, SUM(net) as net_sum
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY tally_group, mis_group
    ORDER BY tally_group, ABS(SUM(net)) DESC
""").fetchall()

# Quick P&L calc
rev = dir_g = dir_i = cos = oh = ind_inc = 0
for r in rows:
    tg = str(r['tally_group'] or '').lower().strip()
    mg = str(r['mis_group']   or '').lower().strip()
    v  = abs(r['net_sum'] or 0)
    if tg == 'sales accounts'  and mg == 'sales accounts': rev    += v
    elif tg == 'direct incomes' and mg == 'direct incomes': dir_g  += v
    elif tg == 'direct incomes':                            dir_i  += v
    elif tg == 'cost of sales :':                           cos    += v
    elif tg == 'indirect incomes':                          ind_inc+= v
    elif tg in ('indirect expenses','salaries and bonus'):
        _COGS = {'direct expenses','opening stock','purchase accounts',
                 'direct incomes','cost of sales :'}
        if mg not in _COGS:                                 oh     += v

dir_inc = max(dir_g, dir_i)
gp  = rev + dir_inc - cos
np_ = gp + ind_inc - oh

print(f"  Revenue  : {rev/1e7:>8.2f} Cr  Tally: 68.00 Cr")
print(f"  Dir Inc  : {dir_inc/1e7:>8.2f} Cr  Tally:  3.93 Cr")
print(f"  COGS     : {cos/1e7:>8.2f} Cr  Tally: 52.45 Cr")
print(f"  GP       : {gp/1e7:>8.2f} Cr  Tally: 19.49 Cr")
print(f"  Ind Inc  : {ind_inc/1e7:>8.2f} Cr  Tally:  0.16 Cr")
print(f"  Overhead : {oh/1e7:>8.2f} Cr  Tally:  7.20 Cr")
print(f"  NP       : {np_/1e7:>8.2f} Cr  Tally: 12.44 Cr")

conn.close()
print("\nDone! Restart portal to see updated values.")
