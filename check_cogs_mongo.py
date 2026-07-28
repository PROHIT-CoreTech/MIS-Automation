"""
Diagnoses the Gross-Profit-near-Revenue bug — MongoDB version, since
this project has already migrated from SQLite to MongoDB.

Uses core/models.py's field names exactly as defined in
migrate_sqlite_to_mongo.py: Company, PLData (company, ledger_name,
tally_group, mis_group, year, month, net).

Run from your project root (venv active):
    python check_cogs_mongo.py
"""
import os
import sys
sys.path.insert(0, '.')

from mongoengine import connect
from core.models import Company, PLData

# ── CONNECT (same pattern as migrate_sqlite_to_mongo.py) ────────
MONGO_URI = None
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('MONGO_URI_DEVELOPMENT='):
                MONGO_URI = line.split('=', 1)[1].strip()
except FileNotFoundError:
    print(".env file not found")

if not MONGO_URI:
    MONGO_URI = os.getenv('MONGO_URI_DEVELOPMENT')

if not MONGO_URI:
    from core.config import MONGO_URI as CONFIG_MONGO_URI
    MONGO_URI = CONFIG_MONGO_URI

print(f"Connecting to: {MONGO_URI[:40]}...")
connect(host=MONGO_URI)

print("=" * 70)
print("0. Companies")
print("=" * 70)
companies = Company.objects()
if not companies:
    print("  ❌ NO companies found in Mongo either. Something else is off —")
    print("     please share core/db.py or wherever the app actually reads")
    print("     company data from now.")
    sys.exit(1)
for c in companies:
    print(f"  id={c.id}  {c.display_name}")

COMPANY = companies[0]  # EDIT: pick the right company if you have more than one
print(f"\nUsing company: {COMPANY.display_name}")

print()
print("=" * 70)
print("1. Mode A — 'cost of sales :' rows, month by month")
print("=" * 70)
rows = PLData.objects(company=COMPANY, tally_group__iexact='cost of sales :').order_by('year', 'month')
if not rows:
    print("  No rows with tally_group='cost of sales :' — Mode A never")
    print("  triggers; COGS always falls back to Mode B for this company.")
else:
    total = 0.0
    for r in rows:
        total += (r.net or 0)
        tag = "← GROUP-TOTAL ROW" if r.ledger_name.strip().lower() == 'cost of sales :' else ""
        print(f"  {r.year}-{r.month:02d}  ledger={r.ledger_name:25s} "
              f"net={r.net:>14,.2f}  {tag}")
    print(f"\n  SUM (what Mode A would use as COGS): {abs(total):,.2f}")

print()
print("=" * 70)
print("2. Mode B — individual COGS buckets")
print("=" * 70)
def bucket_sum(*group_names):
    rows = PLData.objects(company=COMPANY, tally_group__in=list(group_names))
    total = sum(abs(r.net or 0) for r in rows)
    count = rows.count()
    return total, count

opening_total, opening_cnt   = bucket_sum('Opening Stock', 'opening stock')
purch_total, purch_cnt       = bucket_sum('Purchase Accounts', 'purchase accounts',
                                           'Add: Purchase Accounts', 'add: purchase accounts')
direct_total, direct_cnt     = bucket_sum('Direct Expenses', 'direct expenses')
closing_total, closing_cnt   = bucket_sum('Less: Closing Stock', 'less: closing stock',
                                           'Closing Stock', 'closing stock')

print(f"  opening      rows={opening_cnt:>4}  total={opening_total:>16,.2f}")
print(f"  purchases    rows={purch_cnt:>4}  total={purch_total:>16,.2f}")
print(f"  direct_exp   rows={direct_cnt:>4}  total={direct_total:>16,.2f}")
print(f"  closing      rows={closing_cnt:>4}  total={closing_total:>16,.2f}")

mode_b_cogs = opening_total + purch_total + direct_total - closing_total
print(f"\n  Mode B computed COGS: {mode_b_cogs:,.2f}")

print()
print("=" * 70)
print("3. What ledgers exist under 'Direct Expenses' (in case real")
print("   purchase costs are booked there instead)")
print("=" * 70)
rows = PLData.objects(company=COMPANY, tally_group__iexact='direct expenses')
seen = set()
for r in rows:
    if r.ledger_name not in seen:
        seen.add(r.ledger_name)
        print(f"  - {r.ledger_name}")
if not seen:
    print("  (none found)")

print()
print("=" * 70)
print("4. Revenue for comparison")
print("=" * 70)
rev_rows = PLData.objects(company=COMPANY, tally_group__iexact='sales accounts')
rev_total = sum((r.net or 0) for r in rev_rows if r.ledger_name.strip().lower() != 'sales accounts')
print(f"  Revenue (individual sales ledgers only): {abs(rev_total):,.2f}")

print("\nPlease share this full output.")