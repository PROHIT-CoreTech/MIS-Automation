import sys
sys.path.insert(0, '.')

from sync.sync_engine import sync_all
from mongoengine import connect
import os

# connect to MongoDB using same logic as other scripts
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
	print('No MONGO_URI; aborting')
	raise SystemExit(1)
connect(host=MONGO_URI)

from core.models import Tenant
tenant = Tenant.objects().first()
tenant_id = str(tenant.id) if tenant else "1"

print('Starting sync_all (may contact Tally at configured URL)')
res = sync_all(tenant_id=tenant_id)
print('Sync result:', res)
