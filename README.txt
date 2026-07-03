# MIS Portal — Setup Instructions

## Step 1: Install Python
Download from https://python.org (Python 3.11 or 3.12)
During install — CHECK "Add Python to PATH"

## Step 2: Install Dependencies
Open Command Prompt (cmd) in this folder and run:
```
pip install -r requirements.txt
```

## Step 3: Copy Masters.xlsx
Place your Masters.xlsx file in:
```
config/masters/Masters.xlsx
```

## Step 4: Enable Tally HTTP Server
Tally Prime → F12 → Advanced Configuration
→ Act as Server → Enable → Port: 9000 → Accept
Open any one company in Tally

## Step 5: Run the Portal
In Command Prompt:
```
streamlit run app.py
```
Browser will open automatically at http://localhost:8501

## Default Login
Username: admin
Password: admin@123

## Folder Structure
```
mis_portal/
├── app.py              ← Main app (run this)
├── requirements.txt    ← Python packages
├── core/
│   ├── db.py           ← Database layer
│   └── auth.py         ← Login & permissions
├── sync/
│   ├── tally_connect.py   ← Tally HTTP API
│   ├── sync_engine.py     ← Data sync logic
│   └── masters_loader.py  ← Masters.xlsx reader
├── config/
│   └── masters/
│       └── Masters.xlsx   ← Place your file here
└── data/
    └── mis_portal.db   ← Auto-created on first run
```
