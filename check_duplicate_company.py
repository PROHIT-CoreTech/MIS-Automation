"""
Compares the two duplicate 'Unique Steel Products' company records
found in Mongo, to see if data got split between them (likely cause
of the Gross-Profit-near-Revenue bug).

Run from your project root:
    python check_duplicate_company.py
"""
import os
import sys
sys.path.insert(0, '.')

from mongoengine import connect
from core.models import Company, PLData

# ── CONNECT (auto-loads from .env, same as before — no manual paste needed) ──
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

connect(host=MONGO_URI)

# The two duplicate ids found in the previous run
DUPLICATE_IDS = ['6a604a7ea0ea41bc3f494d14', '6a6077e334ec284883909857']

for cid in DUPLICATE_IDS:
    c = Company.objects(id=cid).first()
    if not c:
        print(f"id={cid}  NOT FOUND")
        continue

    all_pl = PLData.objects(company=c)
    total_rows = all_pl.count()

    rev_rows = PLData.objects(company=c, tally_group__iexact='sales accounts')
    revenue = sum((r.net or 0) for r in rev_rows
                  if r.ledger_name.strip().lower() != 'sales accounts')

    direct_exp_rows = PLData.objects(company=c, tally_group__iexact='direct expenses')
    direct_exp = sum((r.net or 0) for r in direct_exp_rows)

    # distinct tally_groups present, so we can see what kind of data each id holds
    groups = sorted(set(r.tally_group for r in all_pl if r.tally_group))

    print("=" * 70)
    print(f"Company id={cid}")
    print(f"  tenant/created_at (if available): {getattr(c, 'created_at', 'n/a')}")
    print(f"  total pl_data rows: {total_rows}")
    print(f"  revenue (sales accounts, individual ledgers): {abs(revenue):,.2f}")
    print(f"  direct expenses total: {abs(direct_exp):,.2f}")
    print(f"  distinct tally_groups present ({len(groups)}):")
    for g in groups:
        print(f"    - {g}")
    print()

print("Please share this full output.")
