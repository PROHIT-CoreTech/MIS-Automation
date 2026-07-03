"""
Run this to verify dashboard calculation is correct:
cd D:\Freelancing\MIS Portal\MIS_Portal
python test_calc.py
"""
import sqlite3, os, sys

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')

# ── EXACT same logic as dashboard._calc ──────────────────
_COGS_NAMES = {
    'direct expenses', 'opening stock', 'purchase accounts',
    'direct incomes',  'cost of sales :'
}

def _is_skip(tg_l, mg_l):
    _HEADERS = {
        'trading account:', 'profit & loss a/c', 'gross profit :',
        'gross profit c/o', 'gross profit b/f', 'nett profit', 'net profit'
    }
    if tg_l in _HEADERS or mg_l in _HEADERS: return True
    if tg_l in ('indirect expenses', 'salaries and bonus', 'salary accounts'):
        if mg_l in _COGS_NAMES: return True
    if tg_l == 'sales accounts' and mg_l == 'sales accounts': return True
    return False

def _calc(rows):
    b = {'revenue':0,'opening':0,'purchases':0,'direct_exp':0,
         'closing':0,'ind_inc':0,'overhead':0}
    cos_net = None
    dir_inc_total = 0
    dir_inc_items = 0

    for r in rows:
        tg  = str(r[0] or '').lower().strip()   # tally_group
        mg  = str(r[1] or '').lower().strip()   # mis_group
        val = abs(r[2] or 0)                    # net

        if _is_skip(tg, mg): continue

        if tg == 'direct incomes':
            if mg == 'direct incomes': dir_inc_total += val
            else:                      dir_inc_items += val
            continue
        if   tg == 'sales accounts':    b['revenue']   += val
        elif tg == 'cost of sales :':   cos_net         = val
        elif tg == 'opening stock':     b['opening']   += val
        elif tg in ('purchase accounts','add: purchase accounts'):
                                        b['purchases'] += val
        elif tg == 'direct expenses':   b['direct_exp']+= val
        elif tg in ('less: closing stock','closing stock'):
                                        b['closing']   += val
        elif tg == 'indirect incomes':  b['ind_inc']   += val
        elif tg in ('indirect expenses','salaries and bonus','salary accounts'):
                                        b['overhead']  += val

    dir_inc = max(dir_inc_total, dir_inc_items)
    cogs    = cos_net if cos_net is not None else (
              b['opening'] + b['purchases'] + b['direct_exp'] - b['closing'])
    gp      = b['revenue'] + dir_inc - cogs
    np_     = gp + b['ind_inc'] - b['overhead']

    return {
        'revenue':  b['revenue'],
        'dir_inc':  dir_inc,
        'cogs':     cogs,
        'gp':       gp,
        'ind_inc':  b['ind_inc'],
        'overhead': b['overhead'],
        'np':       np_,
    }

# ── RUN ──────────────────────────────────────────────────
conn = sqlite3.connect(DB)

cos = conn.execute("SELECT id, tally_name FROM companies").fetchall()

for cid, name in cos:
    print(f"\n{'='*65}")
    print(f"COMPANY: {name}")
    print(f"{'='*65}")

    rows = conn.execute("""
        SELECT tally_group, mis_group, net
        FROM pl_data
        WHERE company_id=?
          AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    """, (cid,)).fetchall()

    if not rows:
        print("  No data for FY25-26")
        continue

    p = _calc(rows)

    print(f"  Revenue   : {p['revenue']/1e7:>8.2f} Cr")
    print(f"  Dir Inc   : {p['dir_inc']/1e7:>8.2f} Cr  (part of GP)")
    print(f"  COGS      : {p['cogs']/1e7:>8.2f} Cr")
    print(f"  ─────────────────────────────")
    print(f"  GP        : {p['gp']/1e7:>8.2f} Cr  ← Expected USP: 19.49")
    print(f"  Ind Inc   : {p['ind_inc']/1e7:>8.2f} Cr")
    print(f"  Overhead  : {p['overhead']/1e7:>8.2f} Cr  ← Expected USP:  7.20")
    print(f"  ─────────────────────────────")
    print(f"  Net Profit: {p['np']/1e7:>8.2f} Cr  ← Expected USP: 12.44")

conn.close()
print("\n\nIf values above are correct but portal shows wrong → cache issue.")
print("Run FORCE_FIX.bat to clear cache completely.")
