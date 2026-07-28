import sys
sys.path.insert(0, '.')
from mongoengine import connect
import os

# load MONGO_URI
MONGO_URI = None
try:
    with open('.env','r') as f:
        for line in f:
            if line.startswith('MONGO_URI_DEVELOPMENT='):
                MONGO_URI = line.split('=',1)[1].strip()
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
    print('No MONGO_URI'); sys.exit(1)
connect(host=MONGO_URI)

from core.models import Company, PLData
from portal_pages import dashboard as dash

candidates = []
for c in Company.objects():
    cnt = PLData.objects(company=c.id).count()
    if cnt > 0:
        candidates.append((c, cnt))

if not candidates:
    print('No company with PL rows found')
    sys.exit(0)

company, cnt = candidates[0]
print('Using company:', company.display_name, str(company.id), 'PL rows=', cnt)

pl_docs = PLData.objects(company=company.id).order_by('year','month')
rows = []
for d in pl_docs:
    rows.append({'ledger_name': d.ledger_name, 'tally_group': d.tally_group,
                 'mis_group': d.mis_group, 'year': d.year, 'month': d.month,
                 'net': d.net, 'month_label': d.month_label})

monthly = dash._monthly(rows)
print('\nSample monthly GP/NP (first 8 months):')
for m in monthly[:8]:
    print(f"{m['month_label']}: Revenue={m['revenue']:.2f}, COGS={m['cogs']:.2f}, GP={m['gp']:.2f}, NP={m['np']:.2f}")

p = dash._calc(rows)
print('\nAggregate (entire dataset):')
print(f"Revenue={p['revenue']:.2f}, COGS={p['cogs']:.2f}, GP={p['gp']:.2f}, NP={p['np']:.2f}")
