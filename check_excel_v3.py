"""Run: python check_excel_v3.py
Auto-detects which company each file belongs to and checks values
"""
import openpyxl, os

folder = os.path.join(os.path.dirname(__file__), 'excel')
files = [
    'PL_Apr-25_to_Mar-26_V11.xlsx',
    'PL_Apr-25_to_Mar-26_V12.xlsx',
    'PL_Apr-25_to_Mar-26_V13.xlsx',
]

TALLY = {
    'USP':          {'Rev': 68.00,  'GP': 19.49, 'OH': 7.20, 'NP': 12.44},
    'Intellichemie':{'Rev': None,   'GP': -0.41, 'OH': 2.23, 'NP': -2.61},
    'Avenuecorp':   {'Rev': 27.91,  'GP': 12.07, 'OH': 6.15, 'NP':  5.93},
}

for fname in files:
    path = os.path.join(folder, fname)
    if not os.path.exists(path):
        print(f"❌ NOT FOUND: {fname}"); continue

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active

    # Read all rows
    rows_data = []
    for row in ws.iter_rows(values_only=True):
        if any(v for v in row):
            rows_data.append(row)

    # Get title row to identify company
    title = str(rows_data[0][0] if rows_data else '').strip()

    # Extract key values
    gp_val = np_val = rev_val = oh_val = None
    sub_count = 0
    for r in rows_data:
        name = str(r[0] or '').strip().upper()
        total = r[-1]
        if not isinstance(total, (int, float)): continue
        if 'GROSS PROFIT' in name and 'NET' not in name:
            gp_val = round(total, 4)
        if 'NET PROFIT' in name:
            np_val = round(total, 4)
        if 'SUB-TOTAL' in name:
            sub_count += 1
            if sub_count == 1:  # First sub-total = Revenue
                rev_val = round(total, 4)
        if 'SUB-TOTAL' in name and sub_count == 4:  # 4th = Overhead
            oh_val = round(total, 4)

    # Detect company
    company = 'Unknown'
    if rev_val and abs(rev_val - 68.00) < 1: company = 'USP'
    elif rev_val and abs(rev_val - 27.91) < 1: company = 'Avenuecorp'
    elif rev_val is None or (rev_val and abs(rev_val) < 1): company = 'Intellichemie'
    elif gp_val and abs(gp_val - (-0.41)) < 0.5: company = 'Intellichemie'

    print(f"\n{'='*60}")
    print(f"FILE: {fname}")
    print(f"DETECTED: {company}")
    print(f"Title: {title[:60]}")
    print(f"\n  Rev={rev_val}  GP={gp_val}  OH={oh_val}  NP={np_val}")

    tally = TALLY.get(company, {})
    if tally:
        print(f"\n  {'':10s} {'EXCEL':>10s}  {'TALLY':>10s}  {'DIFF':>8s}  STATUS")
        print("  " + "-"*48)
        checks = [
            ('GP',  gp_val,  tally.get('GP')),
            ('NP',  np_val,  tally.get('NP')),
            ('OH',  oh_val,  tally.get('OH')),
        ]
        if tally.get('Rev'): checks.insert(0, ('Rev', rev_val, tally.get('Rev')))
        for k, pv, tv in checks:
            if tv is None: continue
            if pv is None:
                print(f"  {k:10s} {'N/A':>10s}  {tv:>10.2f}  {'---':>8s}  ⚠️")
            else:
                diff = pv - tv
                ok = '✅' if abs(diff) < 0.05 else '❌'
                print(f"  {k:10s} {pv:>10.4f}  {tv:>10.4f}  {diff:>+8.4f}  {ok}")
