"""Run: python check_excel_v2.py"""
import openpyxl, os

folder = os.path.join(os.path.dirname(__file__), 'excel')
files = {
    'PL_Apr-25_to_Mar-26_V11.xlsx': {'company': 'Intellichemie', 'tally': {'GP': -0.41, 'OH': 2.23, 'NP': -2.61}},
    'PL_Apr-25_to_Mar-26_V12.xlsx': {'company': 'USP',           'tally': {'Rev': 68.00, 'GP': 19.49, 'OH': 7.20, 'NP': 12.44}},
    'PL_Apr-25_to_Mar-26_V13.xlsx': {'company': 'Avenuecorp',    'tally': {'Rev': 27.91, 'GP': 12.07, 'OH': 6.15, 'NP': 5.93}},
}

for fname, info in files.items():
    path = os.path.join(folder, fname)
    if not os.path.exists(path):
        print(f"❌ NOT FOUND: {fname}")
        continue

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active

    # Extract key rows
    found = {}
    for row in ws.iter_rows(values_only=True):
        if not row or not row[0]: continue
        name = str(row[0]).strip().upper()
        total = row[-1]
        if not isinstance(total, (int, float)): continue
        if 'GROSS PROFIT' in name and 'NET' not in name: found['GP'] = round(total, 4)
        if 'NET PROFIT' in name:                          found['NP'] = round(total, 4)
        if 'SUB-TOTAL' in name and 'GP' not in found and abs(total) > 10: found['Rev'] = round(total, 4)
        if 'INDIRECT EXPENSES' in name and abs(total) > 0: found['OH'] = round(total, 4)

    tally = info['tally']
    print(f"\n{'='*55}")
    print(f"{fname}  [{info['company']}]")
    print(f"{'':15s} {'EXCEL':>10s}  {'TALLY':>10s}  {'DIFF':>8s}  STATUS")
    print("-"*55)
    for k, tv in tally.items():
        pv = found.get(k)
        if pv is None:
            print(f"  {k:13s} {'N/A':>10s}  {tv:>10.2f}  {'---':>8s}  ⚠️")
        else:
            diff = pv - tv
            ok = '✅' if abs(diff) < 0.05 else '❌'
            print(f"  {k:13s} {pv:>10.4f}  {tv:>10.4f}  {diff:>+8.4f}  {ok}")
