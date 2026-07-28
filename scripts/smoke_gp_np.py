import os, sys
sys.path.insert(0, '.')

# Connect to MongoDB
MONGO_URI = None
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('MONGO_URI_DEVELOPMENT='):
                MONGO_URI = line.split('=', 1)[1].strip()
except FileNotFoundError:
    pass

if not MONGO_URI:
    MONGO_URI = os.getenv('MONGO_URI_DEVELOPMENT')

if not MONGO_URI:
    try:
        from core.config import MONGO_URI as CFG
        MONGO_URI = CFG
    except Exception:
        pass

if not MONGO_URI:
    print('No MONGO_URI found; aborting')
    sys.exit(1)

from mongoengine import connect
connect(host=MONGO_URI)

from core.models import Company, PLData
from portal_pages import dashboard as dash

companies = list(Company.objects())
if not companies:
    print('No companies in DB')
    sys.exit(0)

company = companies[0]
print('Using company:', company.display_name, str(company.id))

pl_docs = PLData.objects(company=company.id).order_by('year', 'month')
rows = []
for d in pl_docs:
    rows.append({'ledger_name': d.ledger_name, 'tally_group': d.tally_group,
                 'mis_group': d.mis_group, 'year': d.year, 'month': d.month,
                 'net': d.net})

if not rows:
    print('No PL rows for company')
    sys.exit(0)

# Monthly breakdown using dashboard._monthly
monthly = dash._monthly(rows)
print('\nSample monthly GP/NP (first 8 months):')
for m in monthly[:8]:
    print(f"{m['month_label']}: Revenue={m['revenue']:.2f}, COGS={m['cogs']:.2f}, GP={m['gp']:.2f}, NP={m['np']:.2f}")

# Overall aggregate using dashboard._calc
p = dash._calc(rows)
print('\nAggregate (entire selection):')
print(f"Revenue={p['revenue']:.2f}, COGS={p['cogs']:.2f}, GP={p['gp']:.2f}, NP={p['np']:.2f}")
