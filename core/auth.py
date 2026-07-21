"""
Authentication & Authorization
- bcrypt password hashing
- Role-based access (admin / client)
- Permission checks (excel, ppt)
- Account lockout after N failed attempts
- Admin impersonation

Lockout configuration is sourced from core.config.
"""
import logging
import bcrypt
from datetime import datetime, timedelta

from core.config import MAX_ATTEMPTS, LOCKOUT_MINS, ADMIN_USERNAME, ADMIN_PASSWORD
from core.db import get_conn, get_company_ids_for_user

log = logging.getLogger(__name__)


# ── PASSWORD UTILS ─────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── SESSIONS (Persistent Login) ────────────────────────────────
import secrets

def create_session(user_id: int, hours: int = 24) -> str:
    """Generate a token, store in DB, and return it."""
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + timedelta(hours=hours)).isoformat()
    conn = get_conn()
    conn.execute(
        "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
        (token, user_id, expires_at)
    )
    conn.commit()
    conn.close()
    return token

def get_user_by_session(token: str) -> dict | None:
    """Validate token and return full user dict if valid and active."""
    conn = get_conn()
    session = conn.execute("SELECT * FROM sessions WHERE token=?", (token,)).fetchone()
    if not session:
        conn.close()
        return None
        
    if datetime.now() > datetime.fromisoformat(session['expires_at']):
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))
        conn.commit()
        conn.close()
        return None
        
    # Get user
    user = conn.execute("SELECT * FROM users WHERE id=? AND is_active=1", (session['user_id'],)).fetchone()
    if not user:
        conn.close()
        return None
        
    # Standard login checks
    tenant = None
    if user['tenant_id']:
        tenant = conn.execute("SELECT * FROM tenants WHERE id=?", (user['tenant_id'],)).fetchone()
        if tenant and not tenant['is_active']:
            conn.close()
            return None
            
    company_ids = get_company_ids_for_user(user['id'], user['role'], user['tenant_id'])
    user_dict = dict(user)
    user_dict['company_ids'] = company_ids
    user_dict['tenant'] = dict(tenant) if tenant else None
    conn.close()
    return user_dict

def delete_session(token: str) -> None:
    """Remove session from DB."""
    if not token: return
    conn = get_conn()
    conn.execute("DELETE FROM sessions WHERE token=?", (token,))
    conn.commit()
    conn.close()



# ── CREATE ADMIN (first-time setup) ────────────────────────────
def create_admin_if_not_exists(
    username: str = ADMIN_USERNAME,
    password: str = ADMIN_PASSWORD,
) -> None:
    conn = get_conn()
    existing = conn.execute(
        "SELECT id FROM users WHERE role='super_admin'"
    ).fetchone()
    if not existing:
        # Check if there is an old admin and upgrade its role to super_admin
        old_admin = conn.execute(
            "SELECT id FROM users WHERE username=? AND role='admin'", (username,)
        ).fetchone()
        if old_admin:
            conn.execute(
                "UPDATE users SET role='super_admin', tenant_id=NULL WHERE id=?", (old_admin['id'],)
            )
            log.info("Upgraded existing admin to super_admin: %s", username)
        else:
            conn.execute("""
                INSERT INTO users (username, password_hash, full_name, role,
                                   can_download_excel, can_download_ppt, tenant_id)
                VALUES (?, ?, 'SaaS Super Administrator', 'super_admin', 1, 1, NULL)
            """, (username, hash_password(password)))
            log.info("Super Admin created: %s", username)
        conn.commit()
    conn.close()


# ── LOGIN ──────────────────────────────────────────────────────
def login(username: str, password: str) -> dict | None:
    """
    Returns user dict on success, None on bad credentials.
    Raises PermissionError when account is locked or tenant is suspended.
    """
    conn = get_conn()
    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND is_active=1",
        (username,)
    ).fetchone()

    if not user:
        conn.close()
        return None

    # Check lockout — admin/super_admin are exempt
    if user['locked_until'] and user['role'] not in ('admin', 'super_admin'):
        locked_until = datetime.fromisoformat(user['locked_until'])
        if datetime.now() < locked_until:
            conn.close()
            mins_left = int((locked_until - datetime.now()).seconds / 60) + 1
            raise PermissionError(f"Account locked. Try again in {mins_left} min.")
        else:
            # Lock expired — reset counter
            conn.execute(
                "UPDATE users SET failed_attempts=0, locked_until=NULL WHERE id=?",
                (user['id'],)
            )
            conn.commit()

    # Verify password
    if not verify_password(password, user['password_hash']):
        if user['role'] in ('admin', 'super_admin'):
            conn.close()
            return None

        attempts = user['failed_attempts'] + 1
        if attempts >= MAX_ATTEMPTS:
            locked_until = (datetime.now() + timedelta(minutes=LOCKOUT_MINS)).isoformat()
            conn.execute(
                "UPDATE users SET failed_attempts=?, locked_until=? WHERE id=?",
                (attempts, locked_until, user['id'])
            )
            conn.commit()
            conn.close()
            raise PermissionError(
                f"Too many attempts. Account locked for {LOCKOUT_MINS} minutes."
            )

        conn.execute(
            "UPDATE users SET failed_attempts=? WHERE id=?",
            (attempts, user['id'])
        )
        conn.commit()
        conn.close()
        return None

    # Success — reset failed attempts
    conn.execute(
        "UPDATE users SET failed_attempts=0, locked_until=NULL WHERE id=?",
        (user['id'],)
    )
    conn.commit()

    # Load Tenant Info & check active status
    tenant = None
    if user['tenant_id']:
        tenant = conn.execute(
            "SELECT * FROM tenants WHERE id=?", (user['tenant_id'],)
        ).fetchone()
        if tenant and not tenant['is_active']:
            conn.close()
            raise PermissionError("Your organization account is suspended. Please contact support.")
        if not tenant:
            conn.close()
            raise PermissionError("Tenant configuration not found.")

    company_ids = get_company_ids_for_user(user['id'], user['role'], user['tenant_id'])
    user_dict = dict(user)
    user_dict['company_ids'] = company_ids
    user_dict['tenant'] = dict(tenant) if tenant else None
    conn.close()
    return user_dict


# ── CLIENT MANAGEMENT (Admin) ──────────────────────────────────
def create_client(
    username: str,
    password: str,
    full_name: str,
    company_ids: list,
    can_excel: bool = True,
    can_ppt: bool = False,
    created_by: int | None = None,
    tenant_id: int | None = None,
) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users
            (username, password_hash, full_name, role,
             can_download_excel, can_download_ppt, created_by, tenant_id)
        VALUES (?, ?, ?, 'client', ?, ?, ?, ?)
    """, (username, hash_password(password), full_name,
          int(can_excel), int(can_ppt), created_by, tenant_id))
    user_id = cur.lastrowid
    for cid in company_ids:
        cur.execute(
            "INSERT OR IGNORE INTO user_company_map(user_id, company_id) VALUES(?,?)",
            (user_id, cid)
        )
    conn.commit()
    conn.close()
    return user_id


def update_client_permissions(user_id: int, can_excel: bool, can_ppt: bool) -> None:
    conn = get_conn()
    conn.execute("""
        UPDATE users SET can_download_excel=?, can_download_ppt=?
        WHERE id=?
    """, (int(can_excel), int(can_ppt), user_id))
    conn.commit()
    conn.close()


def update_client_companies(user_id: int, company_ids: list) -> None:
    conn = get_conn()
    conn.execute("DELETE FROM user_company_map WHERE user_id=?", (user_id,))
    for cid in company_ids:
        conn.execute(
            "INSERT OR IGNORE INTO user_company_map(user_id,company_id) VALUES(?,?)",
            (user_id, cid)
        )
    conn.commit()
    conn.close()


def toggle_client_active(user_id: int, active: bool) -> None:
    conn = get_conn()
    conn.execute("UPDATE users SET is_active=? WHERE id=?", (int(active), user_id))
    conn.commit()
    conn.close()


def reset_client_password(user_id: int, new_password: str) -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE users SET password_hash=?, failed_attempts=0, locked_until=NULL WHERE id=?",
        (hash_password(new_password), user_id)
    )
    conn.commit()
    conn.close()


def get_all_clients(tenant_id: int | None = None) -> list:
    conn = get_conn()
    if tenant_id is None:
        rows = conn.execute("""
            SELECT u.id, u.username, u.full_name, u.role,
                   u.can_download_excel, u.can_download_ppt,
                   u.is_active, u.failed_attempts, u.locked_until,
                   u.created_at,
                   GROUP_CONCAT(c.display_name, ', ') as companies
            FROM users u
            LEFT JOIN user_company_map ucm ON ucm.user_id = u.id
            LEFT JOIN companies c ON c.id = ucm.company_id
            WHERE u.role = 'client'
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """).fetchall()
    else:
        rows = conn.execute("""
            SELECT u.id, u.username, u.full_name, u.role,
                   u.can_download_excel, u.can_download_ppt,
                   u.is_active, u.failed_attempts, u.locked_until,
                   u.created_at,
                   GROUP_CONCAT(c.display_name, ', ') as companies
            FROM users u
            LEFT JOIN user_company_map ucm ON ucm.user_id = u.id
            LEFT JOIN companies c ON c.id = ucm.company_id
            WHERE u.role = 'client' AND u.tenant_id = ?
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """, (tenant_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_by_id(user_id: int) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── PERMISSION CHECKS ──────────────────────────────────────────
def can_download_excel(user: dict) -> bool:
    return bool(user.get('can_download_excel', 0)) or user.get('role') in ('admin', 'super_admin')


def can_download_ppt(user: dict) -> bool:
    return bool(user.get('can_download_ppt', 0)) or user.get('role') in ('admin', 'super_admin')


def is_admin(user: dict) -> bool:
    return user.get('role') in ('admin', 'super_admin')


# ── SAAS TENANT CRUD HELPERS ──────────────────────────────────
def create_tenant(name: str, slug: str, plan_name: str, features: list) -> int:
    import json
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tenants (name, slug, plan_name, features, is_active)
        VALUES (?, ?, ?, ?, 1)
    """, (name, slug.lower().strip(), plan_name, json.dumps(features)))
    tenant_id = cur.lastrowid
    conn.commit()
    conn.close()
    return tenant_id


def update_tenant(tenant_id: int, plan_name: str, features: list, is_active: bool) -> None:
    import json
    conn = get_conn()
    conn.execute("""
        UPDATE tenants
        SET plan_name = ?, features = ?, is_active = ?
        WHERE id = ?
    """, (plan_name, json.dumps(features), int(is_active), tenant_id))
    conn.commit()
    conn.close()


def get_all_tenants() -> list:
    conn = get_conn()
    rows = conn.execute("""
        SELECT t.*, 
               (SELECT COUNT(*) FROM users u WHERE u.tenant_id = t.id AND u.role = 'client') as client_count
        FROM tenants t
        ORDER BY t.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_tenant_admin(tenant_id: int, username: str, password: str, full_name: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (username, password_hash, full_name, role, 
                           can_download_excel, can_download_ppt, is_active, tenant_id)
        VALUES (?, ?, ?, 'admin', 1, 1, 1, ?)
    """, (username.lower().strip(), hash_password(password), full_name, tenant_id))
    admin_id = cur.lastrowid
    conn.commit()
    conn.close()
    return admin_id
