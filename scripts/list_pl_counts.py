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

for c in Company.objects():
    cnt = PLData.objects(company=c.id).count()
    print(f"{c.display_name} ({str(c.id)}): PL rows = {cnt}")
