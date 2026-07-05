"""
core/constants.py — Single source of truth for all shared constants.

Previously duplicated across dashboard.py, reports.py, downloads.py,
sync_engine.py. Import from here instead of redefining.
"""

# ── MONTH LABELS ───────────────────────────────────────────────
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# ── TALLY SECTION MAPPING ──────────────────────────────────────
# Maps tally_group (lowercase) → P&L bucket key
# Used by reports.py, downloads.py, sync_engine.py
TALLY_SECTION = {
    'sales accounts':         'revenue',
    'direct incomes':         'dir_inc',
    # COGS sub-groups
    'opening stock':          'opening',
    'purchase accounts':      'purchases',
    'add: purchase accounts': 'purchases',
    'direct expenses':        'direct_exp',
    'less: closing stock':    'closing',
    'closing stock':          'closing',
    'cost of sales :':        'cos_net',
    # P&L
    'indirect incomes':       'ind_inc',
    'indirect expenses':      'overhead',
    'salaries and bonus':     'overhead',
    'salary accounts':        'overhead',
}

# ── TALLY GROUP MAP (dashboard / sync) ────────────────────────
# Maps tally_group (lowercase) → P&L bucket
# Used by dashboard.py and sync_engine.py
TALLY_MAP = {
    # Trading Account — Direct Income
    'direct incomes':         'dir_inc',
    # Trading Account — COGS pre-calculated net
    'cost of sales :':        'cos_net',
    # Trading Account — COGS individual groups
    'opening stock':          'opening',
    'purchase accounts':      'purchases',
    'add: purchase accounts': 'purchases',
    'direct expenses':        'direct_exp',
    'less: closing stock':    'closing',
    'closing stock':          'closing',
    # P&L Account — Indirect
    'indirect incomes':       'ind_inc',
    'indirect expenses':      'overhead',
    'salaries and bonus':     'overhead',
    'salary accounts':        'overhead',
}

# ── TALLY GROUP HEADERS TO SKIP ────────────────────────────────
# These are Tally section divider rows, not actual ledgers.
# Used by sync_engine.py and dashboard.py
SKIP_TALLY_GROUPS = {
    'trading account:', 'cost of sales :', 'income statement:',
    'gross profit :', 'profit & loss a/c', 'gross profit c/o',
    'gross profit b/f', 'nett profit', 'net profit',
}

# ── P&L SECTION DISPLAY ORDER ──────────────────────────────────
# Used by reports.py for rendering the P&L table in correct order
SECTION_ORDER = [
    ('revenue',  '📈 Sales Accounts (Revenue)'),
    ('dir_inc',  '➕ Direct Incomes'),
    ('cogs',     '📦 Cost of Goods Sold'),
    ('gp',       '💹 Gross Profit'),
    ('ind_inc',  '💰 Indirect Incomes'),
    ('overhead', '💸 Indirect Expenses'),
    ('np',       '🏆 Net Profit'),
]

# ── COGS GROUP NAMES ───────────────────────────────────────────
# Valid tally_groups for COGS breakdown. Used in sync_engine.py.
COGS_GROUPS = {
    'opening stock', 'purchase accounts', 'add: purchase accounts',
    'less: closing stock', 'closing stock', 'direct expenses',
}

# ── KNOWN COGS NAMES (dashboard skip-logic) ───────────────────
COGS_NAMES = {
    'direct expenses', 'opening stock', 'purchase accounts',
    'direct incomes',  'cost of sales :',
}

# ── P&L HEADER ROWS (skip these in dashboard rendering) ───────
PL_HEADERS = {
    'trading account:', 'profit & loss a/c', 'gross profit :',
    'gross profit c/o', 'gross profit b/f', 'nett profit', 'net profit',
}
