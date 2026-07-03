"""
Run: python diagnose3.py
Traces EXACT _calc execution step by step for USP
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)

rows = conn.execute("""
    SELECT tally_group, mis_group, net
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
""").fetchall()

print(f"Total rows fetched: {len(rows)}")
print()

_COGS_NAMES = {
    'direct expenses', 'opening stock', 'purchase accounts',
    'direct incomes',  'cost of sales :'
}

b = {'revenue':0,'opening':0,'purchases':0,'direct_exp':0,
     'closing':0,'ind_inc':0,'overhead':0}
cos_net = None
dir_inc_total = 0
dir_inc_items = 0
skipped = []
classified = []

for tg_raw, mg_raw, net in rows:
    tg  = str(tg_raw or '').lower().strip()
    mg  = str(mg_raw or '').lower().strip()
    val = abs(net or 0)

    # _is_skip logic
    _HEADERS = {
        'trading account:', 'profit & loss a/c', 'gross profit :',
        'gross profit c/o', 'gross profit b/f', 'nett profit', 'net profit'
    }
    skip = False
    if tg in _HEADERS or mg in _HEADERS:
        skip = True; reason = "HEADER"
    elif tg in ('indirect expenses','salaries and bonus','salary accounts') and mg in _COGS_NAMES:
        skip = True; reason = f"PARSER_BUG tg={tg} mg={mg}"
    elif tg == 'sales accounts' and mg == 'sales accounts':
        skip = True; reason = "SA_GROUP_TOTAL"

    if skip:
        skipped.append(f"  SKIP [{reason}]: tg='{tg_raw}' mg='{mg_raw}' val={val:,.0f}")
        continue

    # classify
    if tg == 'direct incomes':
        if mg == 'direct incomes':
            dir_inc_total += val
            classified.append(f"  dir_inc_TOTAL: '{tg_raw}'|'{mg_raw}' = {val:,.0f}")
        else:
            dir_inc_items += val
            classified.append(f"  dir_inc_item:  '{tg_raw}'|'{mg_raw}' = {val:,.0f}")
    elif tg == 'sales accounts':
        b['revenue'] += val
        classified.append(f"  REVENUE: '{tg_raw}'|'{mg_raw}' = {val:,.0f}")
    elif tg == 'cost of sales :':
        cos_net = val
        classified.append(f"  COS_NET: '{tg_raw}'|'{mg_raw}' = {val:,.0f}  *** KEY ROW ***")
    elif tg == 'opening stock':
        b['opening'] += val
    elif tg in ('purchase accounts','add: purchase accounts'):
        b['purchases'] += val
    elif tg == 'direct expenses':
        b['direct_exp'] += val
        classified.append(f"  direct_exp: '{tg_raw}'|'{mg_raw}' = {val:,.0f}")
    elif tg in ('less: closing stock','closing stock'):
        b['closing'] += val
    elif tg == 'indirect incomes':
        b['ind_inc'] += val
    elif tg in ('indirect expenses','salaries and bonus','salary accounts'):
        b['overhead'] += val

print("=== SKIPPED ROWS ===")
for s in skipped: print(s)

print("\n=== CLASSIFIED ROWS ===")
for c in classified: print(c)

dir_inc = max(dir_inc_total, dir_inc_items)
cogs    = cos_net if cos_net is not None else (
          b['opening'] + b['purchases'] + b['direct_exp'] - b['closing'])

gp  = b['revenue'] + dir_inc - cogs
np_ = gp + b['ind_inc'] - b['overhead']

print(f"\n=== RESULT ===")
print(f"cos_net set?   : {'YES = ' + str(cos_net) if cos_net else 'NO ← PROBLEM!'}")
print(f"Revenue        : {b['revenue']:>15,.0f} = {b['revenue']/1e7:.2f} Cr")
print(f"dir_inc_total  : {dir_inc_total:>15,.0f} = {dir_inc_total/1e7:.2f} Cr")
print(f"dir_inc_items  : {dir_inc_items:>15,.0f} = {dir_inc_items/1e7:.2f} Cr")
print(f"dir_inc (used) : {dir_inc:>15,.0f} = {dir_inc/1e7:.2f} Cr")
print(f"COGS (cos_net) : {cogs:>15,.0f} = {cogs/1e7:.2f} Cr")
print(f"GP             : {gp:>15,.0f} = {gp/1e7:.2f} Cr  Expected: 19.49")
print(f"Ind Inc        : {b['ind_inc']:>15,.0f} = {b['ind_inc']/1e7:.2f} Cr")
print(f"Overhead       : {b['overhead']:>15,.0f} = {b['overhead']/1e7:.2f} Cr  Expected: 7.20")
print(f"Net Profit     : {np_:>15,.0f} = {np_/1e7:.2f} Cr  Expected: 12.44")

conn.close()
