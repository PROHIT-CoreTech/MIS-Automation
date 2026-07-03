"""
Run: python patch_dashboard.py
Patches dashboard.py _calc() to use net_val (not abs) for group totals
"""
import re, shutil, os

f = os.path.join(os.path.dirname(__file__), 'portal_pages', 'dashboard.py')
shutil.copy(f, f + '.bak')

with open(f) as fh:
    src = fh.read()

# Fix 1: oh_grp abs(net_val) → net_val
src = src.replace(
    'oh_grp       += abs(net_val)   # abs since expense = negative net\n            oh_grp_found  = True',
    'oh_grp       += net_val\n            oh_grp_found  = True'
)

# Fix 2: oh_sal_grp abs(net_val) → net_val
src = src.replace(
    'oh_sal_grp   += abs(net_val)\n            oh_sal_found  = True',
    'oh_sal_grp   += net_val\n            oh_sal_found  = True'
)

# Fix 3: rev_total abs(net_val) → net_val
src = src.replace(
    'rev_total += abs(net_val)',
    'rev_total += net_val'
)

# Fix 4: dir_inc_total abs(net_val) → net_val
src = src.replace(
    'dir_inc_total += abs(net_val)',
    'dir_inc_total += net_val'
)

# Fix 5: dir_inc_items abs(net_val) → val
src = src.replace(
    'dir_inc_items += abs(net_val)',
    'dir_inc_items += val'
)

# Fix 6: cos_net already correct (net_val)

# Fix 7: overhead final calc — ensure abs() applied
old_oh = 'if oh_grp_found or oh_sal_found:\n        overhead = oh_grp + oh_sal_grp\n    else:\n        overhead = oh_items'
new_oh = 'if oh_grp_found or oh_sal_found:\n        overhead = abs(oh_grp) + abs(oh_sal_grp)\n    else:\n        overhead = oh_items'
src = src.replace(old_oh, new_oh)

# Fix 8: dir_inc final calc — ensure abs()
old_di = 'dir_inc = dir_inc_total if dir_inc_total else dir_inc_items'
new_di = 'dir_inc   = abs(dir_inc_total) if dir_inc_total else abs(dir_inc_items)'
src = src.replace(old_di, new_di)

# Fix 9: rev_total final abs
old_rev = '    gp     = rev_total + dir_inc - cogs'
new_rev = '    rev_total = abs(rev_total)\n    gp     = rev_total + dir_inc - cogs'
if 'rev_total = abs(rev_total)' not in src:
    src = src.replace(old_rev, new_rev)

# Fix 10: cogs abs
old_cogs = 'if cos_net_found:\n        cogs = cos_net\n    else:'
new_cogs = 'if cos_net_found:\n        cogs = abs(cos_net)\n    else:'
src = src.replace(old_cogs, new_cogs)

with open(f, 'w') as fh:
    fh.write(src)

# Verify
import ast
ast.parse(src)

# Check key lines
print("Patch applied. Verifying key lines:")
for i, line in enumerate(src.split('\n'), 1):
    if 'net_val' in line or 'rev_total = abs' in line or 'abs(cos_net)' in line or 'abs(oh_grp)' in line:
        print(f"  {i:4d}: {line.strip()}")

print("\n✅ dashboard.py patched successfully!")
print("Now run: python -m streamlit run app.py")
