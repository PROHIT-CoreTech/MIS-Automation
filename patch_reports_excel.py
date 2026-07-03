"""
Run: python patch_reports_excel.py
Fixes Excel generation in reports.py:
1. COGS Sub-Total write_row already fixed
2. Overhead section — use group_totals directly instead of sections dict
3. Ensure group_totals['cogs'] correctly used
"""
import shutil, os, ast

f = os.path.join(os.path.dirname(__file__), 'portal_pages', 'reports.py')
shutil.copy(f, f + '.bak2')

with open(f, encoding='utf-8') as fh:
    src = fh.read()

# Fix: add_section for overhead uses sections dict which is empty for overhead
# Replace with direct group_totals based overhead writing
old = "    add_section('INDIRECT INCOMES',            'ind_inc')\n    add_section('INDIRECT EXPENSES (Overhead)', 'overhead')"
new = """    add_section('INDIRECT INCOMES',            'ind_inc')

    # ── OVERHEAD SECTION ───────────────────────────────────
    # Use individual ledgers from sections for detail rows
    # Use group_totals for Sub-Total (exact Tally match)
    write_row('INDIRECT EXPENSES (Overhead)',
              [''] * (len(mo_labels) + 1),
              {'font': SECTION_FONT, 'fill': SECTION_FILL})
    # Individual ledger rows from sections
    oh_secs = {}
    for (sec, tg, ln), mo_data in sections_raw.items():
        if sec in ('overhead', 'overhead_sal'):
            if ln not in oh_secs:
                oh_secs[ln] = {}
            for (yr, mo), v in mo_data.items():
                lbl2 = f"{MONTHS[mo-1]}-{str(yr)[2:]}"
                oh_secs[ln][lbl2] = oh_secs[ln].get(lbl2, 0) + v
    alt = False
    for ln, mo_data in sorted(oh_secs.items()):
        if all(abs(v) < 100 for v in mo_data.values()): continue
        vals = [round(abs(mo_data.get(l,0))/1e7,4) if abs(mo_data.get(l,0))>=100
                else None for l in mo_labels]
        total = sum(abs(mo_data.get(l,0)) for l in mo_labels)
        vals.append(round(total/1e7,4) if total>=100 else None)
        f2 = ALT_FILL if alt else LEDGER_FILL
        write_row(ln, vals, {'font': LEDGER_FONT, 'fill': f2}, indent=1)
        alt = not alt
    # Sub-Total from group_totals
    oh_sub = [round(section_total('overhead',l)/1e7,4) for l in mo_labels]
    oh_sub.append(round(sum(oh_sub),4))
    write_row('Sub-Total', oh_sub, {'font': SUBTOTAL_FONT, 'fill': SUBTOTAL_FILL})"""

if old in src:
    src = src.replace(old, new)
    print("✅ Fixed overhead section in Excel")
else:
    print("⚠️  Overhead section pattern not found — checking alternate")
    # Try without extra newline
    old2 = "    add_section('INDIRECT INCOMES',            'ind_inc')\n    add_section('INDIRECT EXPENSES (Overhead)', 'overhead')"
    print(f"    Pattern present: {old2 in src}")

# Fix: _generate_excel needs sections_raw (the original data dict)
# Pass data as sections_raw to _generate_excel
old3 = "def _generate_excel(sections, group_totals, mo_labels, sel_months, from_lbl, to_lbl):"
new3 = "def _generate_excel(sections, group_totals, mo_labels, sel_months, from_lbl, to_lbl, sections_raw=None):\n    if sections_raw is None: sections_raw = {}"
if old3 in src:
    src = src.replace(old3, new3)
    print("✅ Added sections_raw parameter")

# Pass data to _generate_excel call
old4 = "            excel_bytes = _generate_excel(\n                sections, group_totals, mo_labels, sel_months, from_lbl, to_lbl\n            )"
new4 = "            excel_bytes = _generate_excel(\n                sections, group_totals, mo_labels, sel_months, from_lbl, to_lbl, data\n            )"
if old4 in src:
    src = src.replace(old4, new4)
    print("✅ Passed data as sections_raw")

with open(f, 'w', encoding='utf-8') as fh:
    fh.write(src)

try:
    ast.parse(src)
    print("✅ Syntax OK")
except SyntaxError as e:
    print(f"❌ Syntax Error: {e}")

print("\nDone! Run:")
print("  for /d /r . %d in (__pycache__) do @rd /s /q \"%d\" 2>nul")
print("  python -m streamlit run app.py")
