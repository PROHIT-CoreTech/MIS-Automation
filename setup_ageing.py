"""
Run ONCE: python setup_ageing.py
Creates ageing_data table in DB
"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)

conn.execute("""
CREATE TABLE IF NOT EXISTS ageing_data (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id  INTEGER NOT NULL,
    party_type  TEXT    NOT NULL,  -- 'customer' or 'vendor'
    party_name  TEXT    NOT NULL,
    bill_ref    TEXT,
    bill_date   TEXT,
    due_date    TEXT,
    amount      REAL    DEFAULT 0,
    days_overdue INTEGER DEFAULT 0,
    synced_at   TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
)
""")
conn.execute("CREATE INDEX IF NOT EXISTS idx_ageing_company ON ageing_data(company_id, party_type)")
conn.commit()
print("✅ ageing_data table created successfully")

# Verify
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(f"Tables in DB: {[t[0] for t in tables]}")
conn.close()
