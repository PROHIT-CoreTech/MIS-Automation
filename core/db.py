"""
Database layer — MongoDB with MongoEngine
"""
import logging
from mongoengine import connect
from core.config import MONGO_URI
from core.models import Tenant, Company, User

log = logging.getLogger(__name__)

DB_READY = False
DB_ERROR = None


def init_db() -> bool:
    """Connect to MongoDB and ensure default data is present."""
    global DB_READY, DB_ERROR

    DB_READY = False
    DB_ERROR = None

    try:
        log.info("Connecting to MongoDB at %s...", MONGO_URI)
        connect(host=MONGO_URI, serverSelectionTimeoutMS=5000)

        # Ensure default tenant exists
        default_tenant = Tenant.objects(slug='default').first()
        if not default_tenant:
            default_tenant = Tenant(
                name='Default Tenant',
                slug='default',
                plan_name='Gold',
                features='["dashboard", "reports", "cash_flow", "downloads", "sync"]',
                is_active=True
            ).save()
            log.info("Created Default Tenant.")

        DB_READY = True
        log.info("MongoDB initialized successfully")
        return True
    except Exception as exc:
        DB_ERROR = str(exc)
        log.exception("MongoDB initialization failed")
        return False


def get_company_ids_for_user(user_id: str, role: str, tenant_id: str | None = None) -> list:
    """
    Super Admin → all active company ids.
    Tenant Admin → only active company ids belonging to their tenant.
    Client → only assigned company ids (which should also be active).
    """
    # Helper to convert ObjectIds to strings
    if role == 'super_admin':
        companies = Company.objects(is_active=True).only('id')
    elif role == 'admin':
        companies = Company.objects(is_active=True, tenant=tenant_id).only('id')
    else:
        user = User.objects(id=user_id).first()
        if user:
            # We filter for active companies among those assigned to the user
            # We can map over the user's companies list
            assigned_ids = [c.id for c in user.companies if c.is_active]
            return assigned_ids
        return []
    
    return [str(c.id) for c in companies]


def get_available_months(company_id: str) -> list:
    """
    Return sorted list of (year, month) tuples available in PLData
    for the given company. Used by the sidebar filter in app.py.
    """
    from core.models import PLData
    from bson import ObjectId
    
    # In MongoDB, we can use distinct or aggregation. 
    # The distinct command can't return pairs easily in PyMongo without aggregation.
    pipeline = [
        {"$match": {"company": ObjectId(company_id)}},
        {"$group": {"_id": {"year": "$year", "month": "$month"}}},
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    
    # We can run pipeline through mongoengine using aggregate
    result = PLData.objects().aggregate(pipeline)
    
    # result is an iterator over dictionaries
    months = [(r['_id']['year'], r['_id']['month']) for r in result]
    return months


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    init_db()
