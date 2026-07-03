"""Run: python check_excel_full.py
Shows EVERY row with value from all 3 Excel files
"""
import openpyxl, os

folder = os.path.join(os.path.dirname(__file__), 'excel')
files = {
    'PL_Apr-25_to_Mar-26_V11.xlsx': 'Avenuecorp',
    'PL_Apr-25_to_Mar-26_V12.xlsx': 'Intellichemie',
    'PL_Apr-25_to_Mar-26_V13.xlsx': 'USP',
}

TALLY = {
    'USP':          {'GP': 19.49, 'OH': 7.20,  'NP': 12.44},
    'Intellichemie':{'GP': -0.41, 'OH': 2.23,  'NP': -2.61},
    'Avenuecorp':   {'GP': 12.07, 'OH': 6.15,  'NP':  5.93},
}

for fname, company in files.items():
    path = os.path.join(folder, fname)
    if not os.path.exists(path):
        print(f"❌ NOT FOUND: {fname}"); continue

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active

    print(f"\n{'='*65}")
    print(f"FILE: {fname}  [{company}]")
    print(f"{'='*65}")
    print(f"{'Row':>4s}  {'Particulars':45s}  {'Total':>10s}")
    print("-"*65)

    for i, row in enumerate(ws.iter_rows(values_only=True), 1):
        if not row or not row[0]: continue
        name = str(row[0] or '').strip()
        total = row[-1]
        if isinstance(total, (int, float)) and total != 0:
            print(f"{i:4d}  {name:45s}  {total:>10.4f}")
        elif name and not isinstance(total, (int, float)):
            print(f"{i:4d}  {name:45s}  {'---':>10s}")

    print(f"\n--- TALLY EXPECTED ---")
    for k,v in TALLY[company].items():
        print(f"  {k}: {v}")
