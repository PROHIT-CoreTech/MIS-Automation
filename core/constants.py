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

# Buckets that represent ASSETS. In this synced data, raw closing_bal
# is stored NEGATIVE for a normal asset balance (verified empirically:
# Cash-in-hand, Bank Accounts, Fixed Assets, Closing Stock all showed
# negative raw values across all 3 companies) — so asset buckets are
# normalised by negating. Everything else (liability/equity buckets)
# keeps its raw sign, since normal liability/equity balances are
# already positive in this data.
CASHFLOW_ASSET_BUCKETS = {
    'cash_bank', 'debtors', 'stock', 'loans_advances_asset', 'deposits',
    'other_current_assets', 'fixed_assets', 'investments',
}

# ── CASH FLOW: HYBRID BS CLASSIFICATION (double-counting fix) ─────
# Tally's Balance Sheet is a NESTED hierarchy. For every section it
# stores BOTH a rolled-up group-total row (ledger_name == the group's
# own name, e.g. "Fixed Assets" = 70.5L) AND the individual member
# ledgers under it (Buildings, Computers, Plant & Machinery … which
# themselves sum to 70.5L). Counting both double-counts every section
# — that was the CFI bug (portal showed 2× the real fixed-asset
# movement).
#
# Fix: prefer the GROUP-TOTAL row (Tally's own accurate rolled-up
# figure) and skip the member ledgers. Only when a bucket has NO
# group-total row in a given month do we fall back to summing member
# ledgers by keyword.
#
# CASHFLOW_GROUP_TOTAL_NAMES: ledger_name (lowercased) → bucket.
# A row whose ledger_name is one of these keys IS that bucket's total.
CASHFLOW_GROUP_TOTAL_NAMES = {
    'fixed assets':                'fixed_assets',
    'investments':                 'investments',
    'sundry debtors':              'debtors',
    'closing stock':               'stock',
    'stock-in-hand':               'stock',
    'sundry creditors':            'creditors',
    'provisions':                  'provisions',
    'duties & taxes':              'duties_taxes',
    'duties &amp; taxes':          'duties_taxes',
    'loans & advances (asset)':    'loans_advances_asset',
    'loans &amp; advances (asset)':'loans_advances_asset',
    'deposits (asset)':            'deposits',
    'capital account':             'capital',
    'loans (liability)':           'loans_liability',
}

# Parent rows that roll up MULTIPLE buckets — must always be skipped,
# never assigned to a bucket (they would double-count their children).
CASHFLOW_PARENT_SKIP = {
    'current assets', 'current liabilities', 'branch / divisions',
    'misc. expenses (asset)', 'misc expenses (asset)',
    'suspense a/c', 'suspence a/c', 'suspense', 'suspence',
    'profit & loss a/c', 'profit &amp; loss a/c',
}

# Fallback member-keyword matching, used ONLY for a bucket that has no
# group-total row in a given month (see presence check per company:
# e.g. company 2 has no 'Investments'/'Deposits (Asset)' group row,
# company 1 has no 'Provisions' group row).
CASHFLOW_MEMBER_KEYWORDS = {
    'investments':          ['investment', 'fixed deposit', 'fd with', 'shares in'],
    'provisions':           ['provision'],
    'deposits':             ['deposit'],
    'duties_taxes':         ['tds', 'tcs', 'esic', 'provident fund',
                             'professional tax', 'pf payable', 'gst', 'duties'],
    'loans_advances_asset': ['loans & advances', 'loans and advances', 'advances'],
}
