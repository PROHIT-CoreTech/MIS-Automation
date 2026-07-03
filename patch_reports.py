"""Run: python patch_reports.py
Patches reports.py group_totals to use net (not abs) so abs() at end is correct
"""
import shutil, os, ast

f = os.path.join(os.path.dirname(__file__), 'portal_pages', 'reports.py')
shutil.copy(f, f + '.bak')

with open(f, encoding='utf-8') as fh:
    src = fh.read()

original_len = len(src)
fixes = []

# Fix 1: overhead group_totals — store net not abs
old1 = "group_totals['overhead'][lbl] = group_totals['overhead'].get(lbl, 0) + abs(val)"
new1 = "group_totals['overhead'][lbl] = group_totals['overhead'].get(lbl, 0) + val"
if old1 in src: src=src.replace(old1,new1); fixes.append('overhead net')

# Fix 2: overhead_sal group_totals — store net not abs
old2 = "group_totals['overhead_sal'][lbl] = group_totals['overhead_sal'].get(lbl, 0) + abs(val)"
new2 = "group_totals['overhead_sal'][lbl] = group_totals['overhead_sal'].get(lbl, 0) + val"
if old2 in src: src=src.replace(old2,new2); fixes.append('overhead_sal net')

# Fix 3: revenue group_totals — store net not abs
old3 = "group_totals['revenue'][lbl] = group_totals['revenue'].get(lbl,0) + abs(val)"
new3 = "group_totals['revenue'][lbl] = group_totals['revenue'].get(lbl,0) + val"
if old3 in src: src=src.replace(old3,new3); fixes.append('revenue net')

# Fix 4: dir_inc_group — store net not abs
old4 = "group_totals['dir_inc_group'][lbl] = group_totals['dir_inc_group'].get(lbl,0) + abs(val)"
new4 = "group_totals['dir_inc_group'][lbl] = group_totals['dir_inc_group'].get(lbl,0) + val"
if old4 in src: src=src.replace(old4,new4); fixes.append('dir_inc_group net')

# Fix 5 & 6: section_total — use abs() on group_total values (tab2)
old5 = "return group_totals['revenue'].get(lbl, 0)\n            if sec_key == 'dir_inc':\n                gt    = group_totals.get('dir_inc_group', {}).get(lbl, 0)"
new5 = "return abs(group_totals['revenue'].get(lbl, 0))\n            if sec_key == 'dir_inc':\n                gt    = abs(group_totals.get('dir_inc_group', {}).get(lbl, 0))"
if old5 in src: src=src.replace(old5,new5); fixes.append('tab2 section_total abs')

# Fix 7 & 8: section_total — overhead abs (tab2)
old6 = "ie_val  = group_totals.get('overhead', {}).get(lbl, 0)\n                sal_val = group_totals.get('overhead_sal', {}).get(lbl, 0)\n                return ie_val + sal_val\n            return sum(abs(v.get(lbl, 0)) for v in sections[sec_key].values())"
new6 = "ie_val  = abs(group_totals.get('overhead', {}).get(lbl, 0))\n                sal_val = abs(group_totals.get('overhead_sal', {}).get(lbl, 0))\n                return ie_val + sal_val\n            return sum(abs(v.get(lbl, 0)) for v in sections[sec_key].values())"
if old6 in src: src=src.replace(old6,new6); fixes.append('tab2 overhead abs')

# Fix 9 & 10: excel section_total abs
old7 = "return group_totals['revenue'].get(lbl, 0)\n        if sec_key == 'dir_inc':\n            gt    = group_totals.get('dir_inc_group', {}).get(lbl, 0)"
new7 = "return abs(group_totals['revenue'].get(lbl, 0))\n        if sec_key == 'dir_inc':\n            gt    = abs(group_totals.get('dir_inc_group', {}).get(lbl, 0))"
if old7 in src: src=src.replace(old7,new7); fixes.append('excel section_total abs')

old8 = "ie_val  = group_totals.get('overhead', {}).get(lbl, 0)\n            sal_val = group_totals.get('overhead_sal', {}).get(lbl, 0)\n            return ie_val + sal_val\n        return sum(abs(v.get(lbl,0)) for v in sections.get(sec_key,{}).values())"
new8 = "ie_val  = abs(group_totals.get('overhead', {}).get(lbl, 0))\n            sal_val = abs(group_totals.get('overhead_sal', {}).get(lbl, 0))\n            return ie_val + sal_val\n        return sum(abs(v.get(lbl,0)) for v in sections.get(sec_key,{}).values())"
if old8 in src: src=src.replace(old8,new8); fixes.append('excel overhead abs')

# monthly chart overhead fix
old9 = "monthly[lbl]['overhead'] = ie_val + sal_val"
new9 = "monthly[lbl]['overhead'] = abs(ie_val) + abs(sal_val)"
if old9 in src: src=src.replace(old9,new9); fixes.append('monthly overhead abs')

with open(f, 'w', encoding='utf-8') as fh:
    fh.write(src)

ast.parse(src)
print(f"Fixes applied ({len(fixes)}):")
for fx in fixes: print(f"  ✅ {fx}")
print(f"\n✅ reports.py patched. Syntax OK.")
print("Run: for /d /r . %d in (__pycache__) do @rd /s /q \"%d\" 2>nul")
print("     python -m streamlit run app.py")
