"""Run: python patch_dashboard.py"""
import re, shutil, os

f = os.path.join(os.path.dirname(__file__), 'portal_pages', 'dashboard.py')
shutil.copy(f, f + '.bak')

with open(f, encoding='utf-8') as fh:
    src = fh.read()

fixes = [
    ('oh_grp       += abs(net_val)   # abs since expense = negative net',
     'oh_grp       += net_val'),
    ('oh_sal_grp   += abs(net_val)',
     'oh_sal_grp   += net_val'),
    ('rev_total += abs(net_val)',
     'rev_total += net_val'),
    ('dir_inc_total += abs(net_val)',
     'dir_inc_total += net_val'),
    ('dir_inc_items += abs(net_val)',
     'dir_inc_items += val'),
    ('if cos_net_found:\n        cogs = cos_net\n    else:',
     'if cos_net_found:\n        cogs = abs(cos_net)\n    else:'),
    ('if oh_grp_found or oh_sal_found:\n        overhead = oh_grp + oh_sal_grp\n    else:\n        overhead = oh_items',
     'if oh_grp_found or oh_sal_found:\n        overhead = abs(oh_grp) + abs(oh_sal_grp)\n    else:\n        overhead = oh_items'),
    ('dir_inc = dir_inc_total if dir_inc_total else dir_inc_items',
     'dir_inc   = abs(dir_inc_total) if dir_inc_total else abs(dir_inc_items)'),
]

count = 0
for old, new in fixes:
    if old in src:
        src = src.replace(old, new)
        count += 1
        print(f"  ✅ Fixed: {old[:50]}...")
    else:
        print(f"  ⚠️  Not found: {old[:50]}...")

# Add rev_total = abs() before gp calculation if not present
if 'rev_total = abs(rev_total)' not in src:
    src = src.replace(
        '    gp     = rev_total + dir_inc - cogs',
        '    rev_total = abs(rev_total)\n    gp     = rev_total + dir_inc - cogs'
    )
    print("  ✅ Added rev_total = abs(rev_total)")

with open(f, 'w', encoding='utf-8') as fh:
    fh.write(src)

import ast
ast.parse(src)
print(f"\n✅ {count} fixes applied. Syntax OK.")
print("Run: python -m streamlit run app.py")
