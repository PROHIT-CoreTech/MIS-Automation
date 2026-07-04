# MIS Portal — Automated Financial Dashboard

A Streamlit-based **Management Information System (MIS) Portal** that automatically syncs financial data from **Tally Prime** and presents it as a live, role-based web dashboard with reports and export capabilities.

---

## ✨ Features

- 📊 **Live Dashboard** — Revenue, Gross Profit, Net Profit KPIs with Plotly charts
- 📄 **MIS Reports** — Detailed monthly P&L breakup with Customer & Vendor Ageing
- 📥 **Downloads** — Formatted Excel (.xlsx) and PowerPoint (.pptx) exports
- 🔄 **Auto Sync** — Pulls P&L, Balance Sheet, and Bill Ageing from Tally Prime via HTTP
- 🔐 **Role-Based Access** — Admin and Client roles with per-company data isolation
- 🔒 **Security** — bcrypt hashing, account lockout, admin impersonation

---

## 🗂️ Project Structure

```
MIS-Automation/
├── app.py                    # Main Streamlit entry point
├── requirements.txt          # Python dependencies
├── config/
│   └── masters/
│       └── Masters.xlsx      # Ledger → MIS Group mapping file
├── core/
│   ├── auth.py               # Authentication, roles, permissions
│   ├── db.py                 # SQLite schema & DB layer
│   └── theme.py              # UI theme, CSS, chart helpers
├── portal_pages/
│   ├── dashboard.py          # KPI charts and P&L summary
│   ├── reports.py            # Detailed P&L + Ageing reports
│   ├── downloads.py          # Excel & PPT export page
│   ├── admin.py              # User management (admin only)
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
- Python 3.10+
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
```

### 4. Run the app
```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

### 5. Default Admin Login
| Field    | Value       |
|----------|-------------|
| Username | `admin`     |
| Password | `admin@123` |

> ⚠️ Change the admin password immediately after first login.

---

## 🔄 Tally Sync Setup

1. Open Tally Prime and load your company
2. Enable HTTP Server: `F12 → Advanced Configuration → Enable ODBC → Port 9000`
3. In the portal, go to **Admin Panel → Sync** and click **Sync Now**

The sync engine will:
- Fetch P&L data (monthly, up to 3 years back on first run)
- Fetch Balance Sheet data
- Fetch Bills Receivable & Payable (Customer / Vendor Ageing)

---

## 👥 User Roles

| Role   | Dashboard | Reports | Downloads | Admin Panel | Sync |
|--------|-----------|---------|-----------|-------------|------|
| Admin  | ✅        | ✅      | ✅        | ✅          | ✅   |
| Client | ✅        | ✅      | ✅ (if permitted) | ❌   | ❌   |

- Clients only see companies assigned to them
- Excel/PPT download can be enabled/disabled per client

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

## 🗄️ Database Tables

| Table            | Description                        |
|------------------|------------------------------------|
| `companies`      | Tally company registry             |
| `users`          | User accounts & permissions        |
| `user_company_map` | Client ↔ Company access control  |
| `pl_data`        | Monthly P&L ledger entries         |
| `bs_data`        | Monthly Balance Sheet entries      |
| `vouchers`       | Sales/Purchase voucher details     |
| `stock_movement` | Monthly inventory movement         |
| `stock_ageing`   | Stock ageing buckets               |
| `ageing_data`    | Bills Receivable / Payable ageing  |
| `outstanding`    | Debtor / Creditor outstanding      |
| `sync_log`       | Sync audit trail                   |

---

## 🔁 Recurring Use (App already set up)

```bash
cd "/Users/rohitbarge/Documents/New Topics/MIS-Automation"
source venv/bin/activate
streamlit run app.py
```