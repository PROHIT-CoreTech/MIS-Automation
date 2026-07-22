import sqlite3
import sys
import os

# Ensure the script can find mongoengine installed in the local venv 
# regardless of which Python binary is executing it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'venv/lib/python3.14/site-packages'))


from mongoengine import connect
from core.models import (
    Tenant, Company, User, Session, PLData, BSData,
    Voucher, StockMovement, StockAgeing, AgeingData,
    Outstanding, CustomReport, SyncLog
)
from datetime import datetime

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

connect(host=MONGO_URI)

def migrate():
    db_path = 'data/mis_portal.db'
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    print("Starting migration...")

    # Clear existing collections to avoid duplicates on re-run
    Tenant.objects.delete()
    Company.objects.delete()
    User.objects.delete()
    Session.objects.delete()
    PLData.objects.delete()
    BSData.objects.delete()
    AgeingData.objects.delete()

    id_map = {
        'tenant': {},
        'company': {},
        'user': {}
    }

    # 1. Migrate Tenants
    cur.execute("SELECT * FROM tenants")
    for row in cur.fetchall():
        tenant = Tenant(
            name=row['name'],
            slug=row['slug'],
            plan_name=row['plan_name'],
            features=row['features'],
            is_active=bool(row['is_active']),
            tally_url=row['tally_url']
        )
        if row['created_at']:
            try:
                tenant.created_at = datetime.fromisoformat(row['created_at'])
            except:
                pass
        tenant.save()
        id_map['tenant'][row['id']] = tenant

    print(f"Migrated {len(id_map['tenant'])} tenants.")

    # 2. Migrate Companies
    cur.execute("SELECT * FROM companies")
    for row in cur.fetchall():
        tenant_doc = id_map['tenant'].get(row['tenant_id'])
        company = Company(
            tally_name=row['tally_name'],
            display_name=row['display_name'],
            company_type=row['company_type'],
            books_from=row['books_from'],
            sync_status=row['sync_status'],
            is_active=bool(row['is_active']),
            tenant=tenant_doc
        )
        
        if row['last_full_sync']:
            company.last_full_sync = row['last_full_sync']
        if row['last_sync']:
            company.last_sync = row['last_sync']
        if row['created_at']:
            try: company.created_at = datetime.fromisoformat(row['created_at'])
            except: pass

        company.save()
        id_map['company'][row['id']] = company

    print(f"Migrated {len(id_map['company'])} companies.")

    # 3. Migrate Users & User Company Map
    cur.execute("SELECT * FROM users")
    users_rows = cur.fetchall()
    
    cur.execute("SELECT * FROM user_company_map")
    ucm_rows = cur.fetchall()
    ucm_map = {}
    for r in ucm_rows:
        ucm_map.setdefault(r['user_id'], []).append(r['company_id'])

    for row in users_rows:
        tenant_doc = id_map['tenant'].get(row['tenant_id'])
        user = User(
            username=row['username'],
            password_hash=row['password_hash'],
            full_name=row['full_name'],
            role=row['role'],
            can_download_excel=bool(row['can_download_excel']),
            can_download_ppt=bool(row['can_download_ppt']),
            is_active=bool(row['is_active']),
            failed_attempts=row['failed_attempts'],
            created_by=row['created_by'],
            tenant=tenant_doc
        )
        if row['locked_until']:
            try: user.locked_until = datetime.fromisoformat(row['locked_until'])
            except: pass
        if row['created_at']:
            try: user.created_at = datetime.fromisoformat(row['created_at'])
            except: pass

        # Assign companies
        user_c_ids = ucm_map.get(row['id'], [])
        user.companies = [id_map['company'][cid] for cid in user_c_ids if cid in id_map['company']]
        
        user.save()
        id_map['user'][row['id']] = user

    print(f"Migrated {len(id_map['user'])} users.")

    # 4. Migrate Sessions
    cur.execute("SELECT * FROM sessions")
    sessions = 0
    for row in cur.fetchall():
        user_doc = id_map['user'].get(row['user_id'])
        if user_doc:
            s = Session(token=row['token'], user=user_doc)
            try:
                if row['created_at']: s.created_at = datetime.fromisoformat(row['created_at'])
                if row['expires_at']: s.expires_at = datetime.fromisoformat(row['expires_at'])
            except: pass
            s.save()
            sessions += 1
    print(f"Migrated {sessions} sessions.")

    # 5. Migrate PL Data
    cur.execute("SELECT * FROM pl_data")
    pl_count = 0
    pl_batch = []
    for row in cur.fetchall():
        comp_doc = id_map['company'].get(row['company_id'])
        if comp_doc:
            pl = PLData(
                company=comp_doc,
                ledger_name=row['ledger_name'],
                tally_group=row['tally_group'],
                mis_group=row['mis_group'],
                year=row['year'],
                month=row['month'],
                month_label=row['month_label'],
                debit=row['debit'],
                credit=row['credit'],
                net=row['net']
            )
            pl_batch.append(pl)
            if len(pl_batch) > 1000:
                PLData.objects.insert(pl_batch)
                pl_batch = []
            pl_count += 1
    if pl_batch:
        PLData.objects.insert(pl_batch)
    print(f"Migrated {pl_count} PLData records.")

    # 6. Migrate BS Data
    cur.execute("SELECT * FROM bs_data")
    bs_count = 0
    bs_batch = []
    for row in cur.fetchall():
        comp_doc = id_map['company'].get(row['company_id'])
        if comp_doc:
            bs = BSData(
                company=comp_doc,
                ledger_name=row['ledger_name'],
                tally_group=row['tally_group'],
                mis_group=row['mis_group'],
                year=row['year'],
                month=row['month'],
                month_label=row['month_label'],
                closing_bal=row['closing_bal']
            )
            bs_batch.append(bs)
            if len(bs_batch) > 1000:
                BSData.objects.insert(bs_batch)
                bs_batch = []
            bs_count += 1
    if bs_batch:
        BSData.objects.insert(bs_batch)
    print(f"Migrated {bs_count} BSData records.")

    # 7. Migrate Ageing Data
    cur.execute("SELECT * FROM ageing_data")
    ad_count = 0
    ad_batch = []
    for row in cur.fetchall():
        comp_doc = id_map['company'].get(row['company_id'])
        if comp_doc:
            ad = AgeingData(
                company=comp_doc,
                party_type=row['party_type'],
                party_name=row['party_name'],
                bill_ref=row['bill_ref'],
                bill_date=row['bill_date'],
                due_date=row['due_date'],
                amount=row['amount'],
                days_overdue=row['days_overdue']
            )
            if row['synced_at']:
                ad.synced_at = row['synced_at']
            ad_batch.append(ad)
            if len(ad_batch) > 1000:
                AgeingData.objects.insert(ad_batch)
                ad_batch = []
            ad_count += 1
    if ad_batch:
        AgeingData.objects.insert(ad_batch)
    print(f"Migrated {ad_count} AgeingData records.")
    
    print("Migration completed successfully!")
    conn.close()

if __name__ == '__main__':
    migrate()
