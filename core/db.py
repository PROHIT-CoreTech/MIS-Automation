"""
Database layer — SQLite (Phase 1)
Phase 2: swap connection string to PostgreSQL, rest stays the same.

DB_PATH and related config are now sourced from core.config.
"""
import sqlite3
import logging
from core.config import DB_PATH

log = logging.getLogger(__name__)


def get_conn() -> sqlite3.Connection:
    """Open and return a WAL-mode SQLite connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create all tables and indexes if they do not already exist."""
    import os
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_conn()
    cur  = conn.cursor()

    # ── TENANTS (SaaS Tenants) ─────────────────────────────────
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tenants'")
    tenants_exists = cur.fetchone()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tenants (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT    NOT NULL,
        slug          TEXT    UNIQUE NOT NULL,
        plan_name     TEXT    NOT NULL DEFAULT 'Silver',
        features      TEXT    NOT NULL DEFAULT '["dashboard", "reports", "downloads", "sync"]',
        is_active     INTEGER DEFAULT 1,
        created_at    TEXT    DEFAULT (datetime('now')),
        tally_url     TEXT    DEFAULT 'http://localhost:9000'
    )""")
    
    if tenants_exists:
        cur.execute("PRAGMA table_info(tenants)")
        tenant_cols = [row[1] for row in cur.fetchall()]
        if 'tally_url' not in tenant_cols:
            cur.execute("ALTER TABLE tenants ADD COLUMN tally_url TEXT DEFAULT 'http://localhost:9000'")

    # Check and add Default Tenant if missing
    cur.execute("SELECT id FROM tenants WHERE id = 1")
    if not cur.fetchone():
        cur.execute("""
        INSERT INTO tenants (id, name, slug, plan_name, features, is_active)
        VALUES (1, 'Default Tenant', 'default', 'Gold', 
                '["dashboard", "reports", "cash_flow", "downloads", "sync"]', 1)
        """)

    # Check if companies table exists and what its constraint is
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='companies'")
    companies_exists = cur.fetchone()

    if companies_exists:
        # Check if index is UNIQUE on tally_name only (old behavior) or if tenant_id is missing
        cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='companies'")
        companies_sql = cur.fetchone()[0]
        if 'UNIQUE(tenant_id, tally_name)' not in companies_sql or 'tenant_id' not in companies_sql:
            # We must migrate companies table
            cur.execute("ALTER TABLE companies RENAME TO companies_old")
            cur.execute("""
            CREATE TABLE companies (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                tally_name    TEXT    NOT NULL,
                display_name  TEXT,
                company_type  TEXT    DEFAULT 'STANDARD',
                books_from    TEXT,
                last_full_sync TEXT,
                last_sync     TEXT,
                sync_status   TEXT    DEFAULT 'pending',
                is_active     INTEGER DEFAULT 1,
                created_at    TEXT    DEFAULT (datetime('now')),
                tenant_id     INTEGER REFERENCES tenants(id),
                UNIQUE(tenant_id, tally_name)
            )""")
            
            # Check if companies_old has tenant_id
            cur.execute("PRAGMA table_info(companies_old)")
            old_company_cols = [row[1] for row in cur.fetchall()]
            if 'tenant_id' in old_company_cols:
                cur.execute("""
                INSERT INTO companies (id, tally_name, display_name, company_type, books_from, 
                                       last_full_sync, last_sync, sync_status, is_active, created_at, tenant_id)
                SELECT id, tally_name, display_name, company_type, books_from, 
                       last_full_sync, last_sync, sync_status, is_active, created_at, tenant_id
                FROM companies_old
                """)
            else:
                cur.execute("""
                INSERT INTO companies (id, tally_name, display_name, company_type, books_from, 
                                       last_full_sync, last_sync, sync_status, is_active, created_at, tenant_id)
                SELECT id, tally_name, display_name, company_type, books_from, 
                       last_full_sync, last_sync, sync_status, is_active, created_at, 1
                FROM companies_old
                """)
            cur.execute("DROP TABLE companies_old")
    else:
        # Create companies table fresh
        cur.execute("""
        CREATE TABLE companies (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            tally_name    TEXT    NOT NULL,
            display_name  TEXT,
            company_type  TEXT    DEFAULT 'STANDARD',
            books_from    TEXT,
            last_full_sync TEXT,
            last_sync     TEXT,
            sync_status   TEXT    DEFAULT 'pending',
            is_active     INTEGER DEFAULT 1,
            created_at    TEXT    DEFAULT (datetime('now')),
            tenant_id     INTEGER REFERENCES tenants(id),
            UNIQUE(tenant_id, tally_name)
        )""")

    # ── USERS (With tenant_id column support) ──────────────────
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    users_exists = cur.fetchone()

    if users_exists:
        cur.execute("PRAGMA table_info(users)")
        user_cols = [row[1] for row in cur.fetchall()]
        if 'tenant_id' not in user_cols:
            cur.execute("ALTER TABLE users ADD COLUMN tenant_id INTEGER REFERENCES tenants(id)")
    else:
        cur.execute("""
        CREATE TABLE users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT    UNIQUE NOT NULL,
            password_hash   TEXT    NOT NULL,
            full_name       TEXT,
            role            TEXT    NOT NULL DEFAULT 'client',
            can_download_excel INTEGER DEFAULT 1,
            can_download_ppt   INTEGER DEFAULT 0,
            is_active       INTEGER DEFAULT 1,
            failed_attempts INTEGER DEFAULT 0,
            locked_until    TEXT,
            created_at      TEXT    DEFAULT (datetime('now')),
            created_by      INTEGER,
            tenant_id       INTEGER REFERENCES tenants(id)
        )""")

    # Fill default tenant_id for existing rows
    cur.execute("UPDATE users SET tenant_id = 1 WHERE tenant_id IS NULL AND role != 'super_admin'")
    cur.execute("UPDATE companies SET tenant_id = 1 WHERE tenant_id IS NULL")

    # ── SESSIONS (Persistent Login) ────────────────────────────────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        token       TEXT PRIMARY KEY,
        user_id     INTEGER NOT NULL REFERENCES users(id),
        created_at  TEXT DEFAULT (datetime('now')),
        expires_at  TEXT NOT NULL
    )""")

    # ── USER ↔ COMPANY MAP (RLS) ───────────────────────────────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_company_map (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL REFERENCES users(id),
        company_id  INTEGER NOT NULL REFERENCES companies(id),
        UNIQUE(user_id, company_id)
    )""")

    # ── P&L DATA ───────────────────────────────────────────────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pl_data (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id   INTEGER NOT NULL REFERENCES companies(id),
        ledger_name  TEXT    NOT NULL,
        tally_group  TEXT,
        mis_group    TEXT,
        year         INTEGER NOT NULL,
        month        INTEGER NOT NULL,
        month_label  TEXT,
        debit        REAL    DEFAULT 0,
        credit       REAL    DEFAULT 0,
        net          REAL    DEFAULT 0,
        updated_at   TEXT    DEFAULT (datetime('now')),
        UNIQUE(company_id, ledger_name, year, month)
    )""")

    # ── BS DATA ────────────────────────────────────────────────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bs_data (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id   INTEGER NOT NULL REFERENCES companies(id),
        ledger_name  TEXT    NOT NULL,
        tally_group  TEXT,
        mis_group    TEXT,
        year         INTEGER NOT NULL,
        month        INTEGER NOT NULL,
        month_label  TEXT,
        closing_bal  REAL    DEFAULT 0,
        updated_at   TEXT    DEFAULT (datetime('now')),
        UNIQUE(company_id, ledger_name, year, month)
    )""")

    # ── VOUCHERS (Sales/Purchase — Brand, State, Item) ─────────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vouchers (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id      INTEGER NOT NULL REFERENCES companies(id),
        voucher_date    TEXT    NOT NULL,
        year            INTEGER,
        month           INTEGER,
        month_label     TEXT,
        voucher_type    TEXT,
        voucher_number  TEXT,
        party_name      TEXT,
        party_state     TEXT,
        item_name       TEXT,
        item_group      TEXT,
        brand           TEXT,
        qty             REAL    DEFAULT 0,
        rate            REAL    DEFAULT 0,
        value           REAL    DEFAULT 0,
        updated_at      TEXT    DEFAULT (datetime('now'))
    )""")

    # ── STOCK MOVEMENT (monthly) ────────────────────────────────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stock_movement (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id   INTEGER NOT NULL REFERENCES companies(id),
        item_name    TEXT    NOT NULL,
        brand        TEXT,
        year         INTEGER NOT NULL,
        month        INTEGER NOT NULL,
        month_label  TEXT,
        open_qty     REAL    DEFAULT 0,
        open_val     REAL    DEFAULT 0,
        in_qty       REAL    DEFAULT 0,
        in_val       REAL    DEFAULT 0,
        out_qty      REAL    DEFAULT 0,
        out_val      REAL    DEFAULT 0,
        close_qty    REAL    DEFAULT 0,
        close_val    REAL    DEFAULT 0,
        updated_at   TEXT    DEFAULT (datetime('now')),
        UNIQUE(company_id, item_name, year, month)
    )""")

    # ── STOCK AGEING ───────────────────────────────────────────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stock_ageing (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id   INTEGER NOT NULL REFERENCES companies(id),
        item_name    TEXT    NOT NULL,
        brand        TEXT,
        sync_date    TEXT    NOT NULL,
        d0_30_qty    REAL    DEFAULT 0,
        d0_30_val    REAL    DEFAULT 0,
        d31_60_qty   REAL    DEFAULT 0,
        d31_60_val   REAL    DEFAULT 0,
        d61_90_qty   REAL    DEFAULT 0,
        d61_90_val   REAL    DEFAULT 0,
        d90p_qty     REAL    DEFAULT 0,
        d90p_val     REAL    DEFAULT 0,
        total_qty    REAL    DEFAULT 0,
        total_val    REAL    DEFAULT 0,
        updated_at   TEXT    DEFAULT (datetime('now'))
    )""")

    # ── AGEING DATA (Bills Receivable / Payable from Tally) ─────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ageing_data (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id   INTEGER NOT NULL REFERENCES companies(id),
        party_type   TEXT    NOT NULL,
        party_name   TEXT    NOT NULL,
        bill_ref     TEXT,
        bill_date    TEXT,
        due_date     TEXT,
        amount       REAL    DEFAULT 0,
        days_overdue INTEGER DEFAULT 0,
        synced_at    TEXT
    )""")

    # ── OUTSTANDING ─────────────────────────────────────────────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS outstanding (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id      INTEGER NOT NULL REFERENCES companies(id),
        party_name      TEXT    NOT NULL,
        party_type      TEXT,
        party_state     TEXT,
        voucher_date    TEXT,
        due_date        TEXT,
        invoice_no      TEXT,
        original_amt    REAL    DEFAULT 0,
        pending_amt     REAL    DEFAULT 0,
        days_overdue    INTEGER DEFAULT 0,
        updated_at      TEXT    DEFAULT (datetime('now'))
    )""")

    # ── CUSTOM REPORTS ──────────────────────────────────────────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS custom_reports (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id  INTEGER REFERENCES companies(id),
        created_by  INTEGER REFERENCES users(id),
        report_name TEXT    NOT NULL,
        group_by    TEXT,
        show_values TEXT,
        filters     TEXT,
        top_n       INTEGER,
        is_active   INTEGER DEFAULT 1,
        created_at  TEXT    DEFAULT (datetime('now'))
    )""")

    # ── SYNC LOG ────────────────────────────────────────────────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sync_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id  INTEGER REFERENCES companies(id),
        sync_type   TEXT,
        status      TEXT,
        records_synced INTEGER DEFAULT 0,
        error_msg   TEXT,
        started_at  TEXT,
        ended_at    TEXT
    )""")

    # ── INDEXES for performance ─────────────────────────────────
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pl_company_month ON pl_data(company_id, year, month)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bs_company_month ON bs_data(company_id, year, month)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_vouchers_company ON vouchers(company_id, year, month)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_vouchers_brand   ON vouchers(company_id, brand)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_vouchers_state   ON vouchers(company_id, party_state)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_stock_company    ON stock_movement(company_id, year, month)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_outstanding_co   ON outstanding(company_id, party_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ageing_company   ON ageing_data(company_id, party_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ucmap_user       ON user_company_map(user_id)")

    conn.commit()
    conn.close()
    log.info("DB initialized successfully")


# ── RLS HELPER ──────────────────────────────────────────────────
def get_company_ids_for_user(user_id: int, role: str, tenant_id: int | None = None) -> list:
    """
    Super Admin → all active company ids.
    Tenant Admin → only active company ids belonging to their tenant.
    Client → only assigned company ids (which should also be active).
    """
    conn = get_conn()
    if role == 'super_admin':
        rows = conn.execute(
            "SELECT id FROM companies WHERE is_active=1"
        ).fetchall()
    elif role == 'admin':
        rows = conn.execute(
            "SELECT id FROM companies WHERE is_active=1 AND tenant_id=?",
            (tenant_id,)
        ).fetchall()
    else:
        rows = conn.execute("""
            SELECT c.id FROM companies c
            JOIN user_company_map ucm ON ucm.company_id = c.id
            WHERE ucm.user_id = ? AND c.is_active = 1
        """, (user_id,)).fetchall()
    conn.close()
    return [r['id'] for r in rows]


def get_available_months(company_id: int) -> list:
    """
    Return sorted list of (year, month) tuples available in pl_data or bs_data
    for the given company. Used by the sidebar filter in app.py.
    """
    conn = get_conn()
    rows = conn.execute(
        "SELECT year, month FROM pl_data WHERE company_id=? "
        "UNION SELECT year, month FROM bs_data WHERE company_id=? "
        "ORDER BY year, month",
        (company_id, company_id)
    ).fetchall()
    conn.close()
    return [(int(r['year']), int(r['month'])) for r in rows]


def company_ids_placeholder(ids: list) -> str:
    """Helper for SQL IN clause: returns comma-separated '?' placeholders."""
    return ','.join('?' * len(ids))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    init_db()
