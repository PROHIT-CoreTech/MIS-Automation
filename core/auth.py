"""
Authentication & Authorization
- bcrypt password hashing
- Role-based access (admin / client)
- Permission checks (excel, ppt)
- Account lockout after N failed attempts
- Admin impersonation
"""
import logging
import bcrypt
import secrets
from datetime import datetime, timedelta

from core.config import MAX_ATTEMPTS, LOCKOUT_MINS, ADMIN_USERNAME, ADMIN_PASSWORD
from core.models import User, Session, Tenant, Company
from core.db import get_company_ids_for_user

log = logging.getLogger(__name__)


# ── HELPER ─────────────────────────────────────────────────────
def doc_to_dict(doc) -> dict:
    if not doc:
        return None
    d = doc.to_mongo().to_dict()
    d['id'] = str(d.pop('_id'))
    
    # Map foreign keys to strings
    if 'tenant' in d and d['tenant']:
        d['tenant_id'] = str(d['tenant'])
    else:
        d['tenant_id'] = None
        
    return d


# ── PASSWORD UTILS ─────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── SESSIONS (Persistent Login) ────────────────────────────────
def create_session(user_id: str, hours: int = 24) -> str:
    """Generate a token, store in DB, and return it."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=hours)
    Session(token=token, user=user_id, expires_at=expires_at).save()
    return token

def get_user_by_session(token: str) -> dict | None:
    """Validate token and return full user dict if valid and active."""
    session = Session.objects(token=token).first()
    if not session:
        return None
        
    if datetime.utcnow() > session.expires_at:
        session.delete()
        return None
        
    user = session.user
    if not user or not user.is_active:
        return None
        
    # Standard login checks
    tenant = user.tenant
    if tenant and not tenant.is_active:
        return None
            
    company_ids = get_company_ids_for_user(str(user.id), user.role, str(tenant.id) if tenant else None)
    
    user_dict = doc_to_dict(user)
    user_dict['company_ids'] = company_ids
    user_dict['tenant'] = doc_to_dict(tenant) if tenant else None
    return user_dict

def delete_session(token: str) -> None:
    """Remove session from DB."""
    if not token: return
    Session.objects(token=token).delete()


# ── CREATE ADMIN (first-time setup) ────────────────────────────
def create_admin_if_not_exists(
    username: str = ADMIN_USERNAME,
    password: str = ADMIN_PASSWORD,
) -> None:
    existing = User.objects(role='super_admin').first()
    if not existing:
        # Check if there is an old admin and upgrade its role to super_admin
        old_admin = User.objects(username=username, role='admin').first()
        if old_admin:
            old_admin.role = 'super_admin'
            old_admin.tenant = None
            old_admin.save()
            log.info("Upgraded existing admin to super_admin: %s", username)
        else:
            User(
                username=username,
                password_hash=hash_password(password),
                full_name='SaaS Super Administrator',
                role='super_admin',
                can_download_excel=True,
                can_download_ppt=True
            ).save()
            log.info("Super Admin created: %s", username)


# ── LOGIN ──────────────────────────────────────────────────────
def login(username: str, password: str) -> dict | None:
    """
    Returns user dict on success, None on bad credentials.
    Raises PermissionError when account is locked or tenant is suspended.
    """
    user = User.objects(username=username, is_active=True).first()

    if not user:
        return None

    # Check lockout — admin/super_admin are exempt
    if user.locked_until and user.role not in ('admin', 'super_admin'):
        if datetime.utcnow() < user.locked_until:
            mins_left = int((user.locked_until - datetime.utcnow()).seconds / 60) + 1
            raise PermissionError(f"Account locked. Try again in {mins_left} min.")
        else:
            # Lock expired — reset counter
            user.failed_attempts = 0
            user.locked_until = None
            user.save()

    # Verify password
    if not verify_password(password, user.password_hash):
        if user.role in ('admin', 'super_admin'):
            return None

        attempts = user.failed_attempts + 1
        if attempts >= MAX_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINS)
            user.failed_attempts = attempts
            user.save()
            raise PermissionError(
                f"Too many attempts. Account locked for {LOCKOUT_MINS} minutes."
            )

        user.failed_attempts = attempts
        user.save()
        return None

    # Success — reset failed attempts
    user.failed_attempts = 0
    user.locked_until = None
    user.save()

    # Load Tenant Info & check active status
    tenant = user.tenant
    if tenant:
        if not tenant.is_active:
            raise PermissionError("Your organization account is suspended. Please contact support.")

    company_ids = get_company_ids_for_user(str(user.id), user.role, str(tenant.id) if tenant else None)
    
    user_dict = doc_to_dict(user)
    user_dict['company_ids'] = company_ids
    user_dict['tenant'] = doc_to_dict(tenant) if tenant else None
    return user_dict


# ── CLIENT MANAGEMENT (Admin) ──────────────────────────────────
def create_client(
    username: str,
    password: str,
    full_name: str,
    company_ids: list,
    can_excel: bool = True,
    can_ppt: bool = False,
    created_by: str | None = None,
    tenant_id: str | None = None,
) -> str:
    user = User(
        username=username,
        password_hash=hash_password(password),
        full_name=full_name,
        role='client',
        can_download_excel=can_excel,
        can_download_ppt=can_ppt,
        created_by=created_by,
        tenant=tenant_id,
        companies=company_ids
    ).save()
    return str(user.id)


def update_client_permissions(user_id: str, can_excel: bool, can_ppt: bool) -> None:
    User.objects(id=user_id).update(
        set__can_download_excel=can_excel,
        set__can_download_ppt=can_ppt
    )


def update_client_companies(user_id: str, company_ids: list) -> None:
    User.objects(id=user_id).update(set__companies=company_ids)


def toggle_client_active(user_id: str, active: bool) -> None:
    User.objects(id=user_id).update(set__is_active=active)


def reset_client_password(user_id: str, new_password: str) -> None:
    User.objects(id=user_id).update(
        set__password_hash=hash_password(new_password),
        set__failed_attempts=0,
        set__locked_until=None
    )


def get_all_clients(tenant_id: str | None = None) -> list:
    if tenant_id:
        users = User.objects(role='client', tenant=tenant_id).order_by('-created_at')
    else:
        users = User.objects(role='client').order_by('-created_at')
        
    results = []
    for u in users:
        d = doc_to_dict(u)
        d['companies'] = ", ".join([c.display_name for c in u.companies if c.display_name]) if u.companies else ""
        results.append(d)
    return results


def get_user_by_id(user_id: str) -> dict | None:
    user = User.objects(id=user_id).first()
    return doc_to_dict(user)


# ── PERMISSION CHECKS ──────────────────────────────────────────
def can_download_excel(user: dict) -> bool:
    return bool(user.get('can_download_excel', False)) or user.get('role') in ('admin', 'super_admin')


def can_download_ppt(user: dict) -> bool:
    return bool(user.get('can_download_ppt', False)) or user.get('role') in ('admin', 'super_admin')


def is_admin(user: dict) -> bool:
    return user.get('role') in ('admin', 'super_admin')


# ── SAAS TENANT CRUD HELPERS ──────────────────────────────────
def create_tenant(name: str, slug: str, plan_name: str, features: list) -> str:
    import json
    tenant = Tenant(
        name=name,
        slug=slug.lower().strip(),
        plan_name=plan_name,
        features=json.dumps(features),
        is_active=True
    ).save()
    return str(tenant.id)


def update_tenant(tenant_id: str, plan_name: str, features: list, is_active: bool) -> None:
    import json
    Tenant.objects(id=tenant_id).update(
        set__plan_name=plan_name,
        set__features=json.dumps(features),
        set__is_active=is_active
    )


def get_all_tenants() -> list:
    tenants = Tenant.objects().order_by('-created_at')
    results = []
    for t in tenants:
        d = doc_to_dict(t)
        d['client_count'] = User.objects(tenant=t, role='client').count()
        results.append(d)
    return results


def create_tenant_admin(tenant_id: str, username: str, password: str, full_name: str) -> str:
    admin = User(
        username=username.lower().strip(),
        password_hash=hash_password(password),
        full_name=full_name,
        role='admin',
        can_download_excel=True,
        can_download_ppt=True,
        is_active=True,
        tenant=tenant_id
    ).save()
    return str(admin.id)
