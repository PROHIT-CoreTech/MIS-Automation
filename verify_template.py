"""Run: python verify_template.py
Checks which template ledgers exist in DB vs which are missing"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# Get all USP ledgers
db_ledgers = {}
rows = conn.execute("""
    SELECT ledger_name, tally_group, mis_group, SUM(net) as total
    FROM pl_data WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY ledger_name, tally_group, mis_group
""").fetchall()
for r in rows:
    db_ledgers[r['ledger_name']] = {
        'tg': r['tally_group'], 'mg': r['mis_group'], 'val': r['total']
    }

# Template sections to check
template_ledgers = {
    # REVENUE
    "GST SALES": "Sales Accounts",
    "IGST SALES": "Sales Accounts",
    "EXPORT SALES": "Sales Accounts",
    "Goods Sold As Free of Cost": "Sales Accounts",
    "Sales Bills to Make": "Sales Accounts",
    "AMC Service Charges": "Direct Incomes",
    "Foundation Scheme Income": "Direct Incomes",
    "Freight Outword": "Direct Incomes",
    "Installation Charges": "Direct Incomes",
    "Job Work Charges Received": "Direct Incomes",
    "Packing Charges": "Direct Incomes",
    "Service Charges": "Direct Incomes",
    "Turnover Discount": "Direct Incomes",
    # COGS
    "IGST Purchase @18%": "Purchase Accounts",
    "Local GST Purchase @ 18 %": "Purchase Accounts",
    "Purchase - GST (Local)": "Purchase Accounts",
    "Purchase - IGST (Inter State)": "Purchase Accounts",
    "Purchase - Import": "Purchase Accounts",
    "Purchase Bills to Come": "Purchase Accounts",
    "AMC Charge Paid": "Direct Expenses",
    "Customs Duty": "Direct Expenses",
    "Freight & Clearing Agent Charges - Import": "Direct Expenses",
    "Freight Inward": "Direct Expenses",
    "Installation Charges Paid": "Direct Expenses",
    "Insurance Charge": "Direct Expenses",
    "Job Work Charges Paid": "Direct Expenses",
    "Packing Charges Paid": "Direct Expenses",
    "Service Charge Paid": "Direct Expenses",
    "Opening Stock": "Opening Stock",
    # INDIRECT EXPENSES
    "Salaries & Wages": "Salaries and Bonus",
    "Co's Contribution to EPFO": "Salaries and Bonus",
    "Co's Contribution to ESIC": "Salaries and Bonus",
    "Consultancy Charge": "Indirect Expenses",
    "Commission Paid": "Indirect Expenses",
    "Depreciation": "Indirect Expenses",
    "Partner Remuneration": "Indirect Expenses",
    "Sundry Balance Write Off": "Indirect Expenses",
    "Interest / Penalty - Statutory": "Indirect Expenses",
}

print(f"{'Ledger':50s} {'Expected TG':25s} {'DB TG':25s} {'Value':>12s} {'Match'}")
print("-"*120)

found = missing = wrong_tg = 0
for ledger, expected_tg in template_ledgers.items():
    if ledger in db_ledgers:
        db = db_ledgers[ledger]
        match = '✅' if db['tg'] == expected_tg else '⚠️ WRONG TG'
        if db['tg'] == expected_tg: found += 1
        else: wrong_tg += 1
        print(f"  {ledger:48s} {expected_tg:25s} {db['tg']:25s} {db['val']/1e7:>10.4f}Cr {match}")
    else:
        missing += 1
        print(f"  {ledger:48s} {expected_tg:25s} {'❌ NOT IN DB':25s} {'':>12s}")

print(f"\nSummary: Found={found}, Missing={missing}, Wrong TG={wrong_tg}")
print(f"\nMISSING = Need re-sync to get these ledgers")
conn.close()
