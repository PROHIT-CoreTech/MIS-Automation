# MIS Portal — Multi-Tenant SaaS Financial Dashboard

A Streamlit-based **Management Information System (MIS) Portal** that automatically syncs financial data from **Tally Prime** and presents it as a live, role-based web dashboard. Designed with a multi-tenant SaaS architecture supporting subdomains for isolated client workspaces.

---

## ✨ Features

- 🏢 **Multi-Tenant SaaS Architecture** — Subdomain-based routing (e.g., `client.localhost:8501`) for complete data isolation and branded login pages.
- 👑 **Super Admin Dashboard** — Centralized management of tenants, tenant feature gating, and system overview.
- 📊 **Live Dashboard & KPI** — Revenue, Gross Profit, Net Profit KPIs with Plotly charts.
- 📄 **MIS Reports** — Detailed monthly P&L breakup with Customer & Vendor Ageing.
- 💸 **Cash Flow** — Track inflows, outflows, and cash balances efficiently.
- 📥 **Downloads** — Formatted Excel (.xlsx) and PowerPoint (.pptx) exports.
- 🔄 **Auto Sync** — Pulls P&L, Balance Sheet, and Bill Ageing from Tally Prime via HTTP.
- 🔐 **Role-Based Access** — Super Admin, Admin, and Client roles with granular access controls.
- 🔒 **Security** — bcrypt hashing, tenant gating, account lockout, admin impersonation.
- 🌍 **Landing Page** — Marketing landing page for new visitors on the base domain.

---

## 🆕 Recent Updates
- **UI Modernization**: Upgraded legacy bar charts to sleek, modern Donut charts (with dynamic center annotations) for SaaS Revenue tracking.
- **Performance Optimization**: Hoisted rendering dictionaries and imports to the global scope across the SaaS Admin portal to significantly improve Streamlit hot-reload performance.
- **Deprecation Cleanup**: Migrated entirely to Streamlit's new `width="stretch"` standard, eliminating all `use_container_width` terminal warnings.
- **Form State Fixes**: Implemented native `st.form` capabilities for tenant creation to ensure smooth input clearing without premature `st.rerun()` resets.

---

## 🗂️ Project Structure

```text
MIS-Automation/
├── app.py                    # Main Streamlit entry point & Subdomain Router
├── requirements.txt          # Python dependencies
├── config/
│   └── masters/
│       └── Masters.xlsx      # Ledger → MIS Group mapping file
├── core/
│   ├── auth.py               # Authentication, roles, permissions
│   ├── db.py                 # SQLite schema & DB layer
│   ├── theme.py              # UI theme, CSS, chart helpers
│   └── subdomain.py          # Tenant routing & subdomain detection
├── portal_pages/
│   ├── landing.py            # Marketing landing page (Base domain)
│   ├── login.py              # Tenant-specific and Super Admin login
│   ├── dashboard.py          # KPI charts and P&L summary
│   ├── reports.py            # Detailed P&L + Ageing reports
│   ├── cash_flow.py          # Cash flow visualization
│   ├── downloads.py          # Excel & PPT export page
│   ├── admin.py              # Tenant User management (admin only)
│   ├── saas_admin.py         # Super Admin tenant management
│   ├── sidebar.py            # Navigation & context switching
│   └── sync_status.py        # Sync status viewer (admin only)
├── sync/
│   ├── sync_engine.py        # Tally sync: P&L, BS, Ageing
│   ├── tally_connect.py      # Tally Prime HTTP/XML API client
│   └── masters_loader.py     # Masters.xlsx loader & auto-classifier
└── data/
    └── mis_portal.db         # SQLite database (auto-created)
```

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.11 or 3.12 (Highly recommended for stability. Avoid alpha/beta builds like 3.14 which may cause segmentation faults with pandas/numpy)
- Tally Prime running on `localhost:9000` (for sync features)

### 1. Clone / Navigate to the project
```bash
cd "/Users/rohitbarge/Documents/New Topics/MIS-Automation"
```

### 2. Create & activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install watchdog  # Recommended for better Streamlit hot-reload performance
```

### 4. Run the app
```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser to view the **Landing Page**.

### 5. Default Super Admin Login
Access the Super Admin login from the base domain (e.g., via the Admin button on the landing page) to manage tenants:
| Field    | Value       |
|----------|-------------|
| Username | `admin`     |
| Password | `admin@123` |

> ⚠️ Change the super admin password immediately after first login.

---

## 🏢 Subdomains & Tenants

The portal operates on a subdomain-per-tenant basis.
- **Base Domain (`localhost:8501`)**: Displays the landing page and provides Super Admin login.
- **Tenant Subdomain (`<tenant-slug>.localhost:8501`)**: Provides tenant-specific login, dashboard, reports, and sync functionality.

*Note: For local testing, you may need to configure your `hosts` file to resolve `*.localhost` if your OS does not support it natively, though most modern browsers handle `*.localhost` out of the box.*

---

## 🔄 Tally Sync Setup

1. Open Tally Prime and load your company
2. Enable HTTP Server: `F12 → Advanced Configuration → Enable ODBC → Port 9000`
3. Log in to a tenant portal as an Admin.
4. Go to **Admin Panel → Sync** and click **Sync Now**

The sync engine will:
- Fetch P&L data (monthly, up to 3 years back on first run)
- Fetch Balance Sheet data
- Fetch Bills Receivable & Payable (Customer / Vendor Ageing)

---

## 👥 User Roles

| Role          | Domain scope       | Dashboard | Reports | Cash Flow | Downloads | Tenant Admin | SaaS Admin |
|---------------|--------------------|-----------|---------|-----------|-----------|--------------|------------|
| **Super Admin**| Base Domain        | ✅        | ✅      | ✅        | ✅        | ✅           | ✅         |
| **Admin**      | Tenant Subdomain   | ✅        | ✅      | ✅        | ✅        | ✅           | ❌         |
| **Client**     | Tenant Subdomain   | ✅        | ✅      | ✅        | ✅ (if enabled)| ❌      | ❌         |

- Tenant features (Dashboard, Reports, Cash Flow, Downloads, Sync) can be toggled per tenant by the Super Admin.
- Clients only see companies assigned to them within their tenant environment.

---

## 📦 Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Frontend    | Streamlit 1.45 + custom CSS         |
| Charts      | Plotly 6                            |
| Data        | Pandas 2.2                          |
| Database    | SQLite (WAL mode, PostgreSQL-ready) |
| Auth        | bcrypt                              |
| Excel       | openpyxl                            |
| PowerPoint  | python-pptx                         |
| Tally API   | HTTP/XML (TDL)                      |

---

## 🗄️ Database Tables (Overview)

- `tenants`: Multi-tenant routing configurations (slug, features, status)
- `companies`: Tally company registry (per tenant)
- `users`: User accounts & roles (Super Admin, Admin, Client)
- `user_company_map`: Client ↔ Company access control
- `pl_data`, `bs_data`: Financial ledgers
- `vouchers`, `stock_movement`, `stock_ageing`: Vouchers and Inventory
- `ageing_data`, `outstanding`: Debtor/Creditor data
- `sync_log`: Audit trails

---

## 🔁 Recurring Use (App already set up)

```bash
cd "/Users/rohitbarge/Documents/New Topics/MIS-Automation"
source venv/bin/activate
streamlit run app.py
```