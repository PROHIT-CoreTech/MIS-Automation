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


# ── CREATE ADMIN (first-time setup) ────────────────────────────
def create_admin_if_not_exists(
    username: str = ADMIN_USERNAME,
    password: str = ADMIN_PASSWORD,
) -> None:
    conn = get_conn()
    existing = conn.execute(
        "SELECT id FROM users WHERE role='admin'"
    ).fetchone()
    if not existing:
        conn.execute("""
            INSERT INTO users (username, password_hash, full_name, role,
                               can_download_excel, can_download_ppt)
            VALUES (?, ?, 'Administrator', 'admin', 1, 1)
        """, (username, hash_password(password)))
        conn.commit()
        log.info("Admin created: %s", username)
    conn.close()


# ── LOGIN ──────────────────────────────────────────────────────
def login(username: str, password: str) -> dict | None:
    """
    Returns user dict on success, None on bad credentials.
    Raises PermissionError when account is locked.
    """
    conn = get_conn()
    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND is_active=1",
        (username,)
    ).fetchone()

    if not user:
        conn.close()
        return None

    # Check lockout — admin is exempt
    if user['locked_until'] and user['role'] != 'admin':
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
        if user['role'] == 'admin':
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

    company_ids = get_company_ids_for_user(user['id'], user['role'])
    user_dict = dict(user)
    user_dict['company_ids'] = company_ids
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
) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users
            (username, password_hash, full_name, role,
             can_download_excel, can_download_ppt, created_by)
        VALUES (?, ?, ?, 'client', ?, ?, ?)
    """, (username, hash_password(password), full_name,
          int(can_excel), int(can_ppt), created_by))
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


def get_all_clients() -> list:
    conn = get_conn()
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
    conn.close()
    return [dict(r) for r in rows]


def get_user_by_id(user_id: int) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── PERMISSION CHECKS ──────────────────────────────────────────
def can_download_excel(user: dict) -> bool:
    return bool(user.get('can_download_excel', 0)) or user.get('role') == 'admin'


def can_download_ppt(user: dict) -> bool:
    return bool(user.get('can_download_ppt', 0)) or user.get('role') == 'admin'


def is_admin(user: dict) -> bool:
    return user.get('role') == 'admin'
