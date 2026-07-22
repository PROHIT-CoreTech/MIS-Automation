from datetime import datetime
from mongoengine import (
    Document, StringField, BooleanField, DateTimeField, 
    ReferenceField, IntField, FloatField, ListField, 
    DynamicDocument
)

class Tenant(Document):
    name = StringField(required=True)
    slug = StringField(required=True, unique=True)
    plan_name = StringField(default='Silver')
    features = StringField(default='["dashboard", "reports", "downloads", "sync"]')
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    tally_url = StringField(default='http://localhost:9000')

class Company(Document):
    tally_name = StringField(required=True)
    display_name = StringField()
    company_type = StringField(default='STANDARD')
    books_from = StringField()
    last_full_sync = StringField()
    last_sync = StringField()
    sync_status = StringField(default='pending')
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    tenant = ReferenceField(Tenant)

    meta = {
        'indexes': [
            {'fields': ('tenant', 'tally_name'), 'unique': True}
        ]
    }

class User(Document):
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    full_name = StringField()
    role = StringField(default='client')
    can_download_excel = BooleanField(default=True)
    can_download_ppt = BooleanField(default=False)
    is_active = BooleanField(default=True)
    failed_attempts = IntField(default=0)
    locked_until = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    created_by = ReferenceField('self')
    tenant = ReferenceField(Tenant)
    
    # Replacement for user_company_map
    companies = ListField(ReferenceField(Company), default=list)

class Session(Document):
    token = StringField(required=True, primary_key=True)
    user = ReferenceField(User, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(required=True)

class PLData(Document):
    company = ReferenceField(Company, required=True)
    ledger_name = StringField(required=True)
    tally_group = StringField()
    mis_group = StringField()
    year = IntField(required=True)
    month = IntField(required=True)
    month_label = StringField()
    debit = FloatField(default=0)
    credit = FloatField(default=0)
    net = FloatField(default=0)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'indexes': [
            {'fields': ('company', 'ledger_name', 'year', 'month'), 'unique': True},
            ('company', 'year', 'month')
        ]
    }

class BSData(Document):
    company = ReferenceField(Company, required=True)
    ledger_name = StringField(required=True)
    tally_group = StringField()
    mis_group = StringField()
    year = IntField(required=True)
    month = IntField(required=True)
    month_label = StringField()
    closing_bal = FloatField(default=0)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'indexes': [
            {'fields': ('company', 'ledger_name', 'year', 'month'), 'unique': True},
            ('company', 'year', 'month')
        ]
    }

class Voucher(Document):
    company = ReferenceField(Company, required=True)
    voucher_date = StringField(required=True)
    year = IntField()
    month = IntField()
    month_label = StringField()
    voucher_type = StringField()
    voucher_number = StringField()
    party_name = StringField()
    party_state = StringField()
    item_name = StringField()
    item_group = StringField()
    brand = StringField()
    qty = FloatField(default=0)
    rate = FloatField(default=0)
    value = FloatField(default=0)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'indexes': [
            ('company', 'year', 'month'),
            ('company', 'brand'),
            ('company', 'party_state')
        ]
    }

class StockMovement(Document):
    company = ReferenceField(Company, required=True)
    item_name = StringField(required=True)
    brand = StringField()
    year = IntField(required=True)
    month = IntField(required=True)
    month_label = StringField()
    open_qty = FloatField(default=0)
    open_val = FloatField(default=0)
    in_qty = FloatField(default=0)
    in_val = FloatField(default=0)
    out_qty = FloatField(default=0)
    out_val = FloatField(default=0)
    close_qty = FloatField(default=0)
    close_val = FloatField(default=0)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'indexes': [
            {'fields': ('company', 'item_name', 'year', 'month'), 'unique': True},
            ('company', 'year', 'month')
        ]
    }

class StockAgeing(Document):
    company = ReferenceField(Company, required=True)
    item_name = StringField(required=True)
    brand = StringField()
    sync_date = StringField(required=True)
    d0_30_qty = FloatField(default=0)
    d0_30_val = FloatField(default=0)
    d31_60_qty = FloatField(default=0)
    d31_60_val = FloatField(default=0)
    d61_90_qty = FloatField(default=0)
    d61_90_val = FloatField(default=0)
    d90p_qty = FloatField(default=0)
    d90p_val = FloatField(default=0)
    total_qty = FloatField(default=0)
    total_val = FloatField(default=0)
    updated_at = DateTimeField(default=datetime.utcnow)

class AgeingData(Document):
    company = ReferenceField(Company, required=True)
    party_type = StringField(required=True)
    party_name = StringField(required=True)
    bill_ref = StringField()
    bill_date = StringField()
    due_date = StringField()
    amount = FloatField(default=0)
    days_overdue = IntField(default=0)
    synced_at = StringField()

    meta = {
        'indexes': [
            ('company', 'party_type')
        ]
    }

class Outstanding(Document):
    company = ReferenceField(Company, required=True)
    party_name = StringField(required=True)
    party_type = StringField()
    party_state = StringField()
    voucher_date = StringField()
    due_date = StringField()
    invoice_no = StringField()
    original_amt = FloatField(default=0)
    pending_amt = FloatField(default=0)
    days_overdue = IntField(default=0)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'indexes': [
            ('company', 'party_type')
        ]
    }

class CustomReport(Document):
    company = ReferenceField(Company)
    created_by = ReferenceField(User)
    report_name = StringField(required=True)
    group_by = StringField()
    show_values = StringField()
    filters = StringField()
    top_n = IntField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

class SyncLog(Document):
    company = ReferenceField(Company)
    sync_type = StringField()
    status = StringField()
    records_synced = IntField(default=0)
    error_msg = StringField()
    started_at = StringField()
    ended_at = StringField()
