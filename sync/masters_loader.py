"""
Masters.xlsx Loader
- Single file for all clients
- Col A = Ledger Name, Col B = Tally Group, Col C = MIS Group
- Fallback to Tally native group if ledger not in Masters
"""
import os
import openpyxl

MASTERS_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'config', 'masters', 'Masters.xlsx'
)

_cache: dict = {}   # in-memory cache

def load_masters(force_reload=False) -> dict:
    """
    Returns: { ledger_name: {'tally_group': ..., 'mis_group': ...} }
    """
    global _cache
    if _cache and not force_reload:
        return _cache

    if not os.path.exists(MASTERS_PATH):
        print(f"[Masters] File not found: {MASTERS_PATH}")
        return {}

    wb  = openpyxl.load_workbook(MASTERS_PATH, data_only=True)
    ws  = wb.active
    mapping = {}

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or len(row) < 2:
            continue
        ledger      = str(row[0] or '').strip()
        tally_grp   = str(row[1] or '').strip()
        mis_grp     = str(row[2] or '').strip() if len(row) > 2 else tally_grp

        if not ledger:
            continue
        if tally_grp in ('MIS Grouping', 'Tally Grouping', ''):
            continue

        mapping[ledger] = {
            'tally_group': tally_grp,
            'mis_group':   mis_grp if mis_grp else tally_grp
        }

    _cache = mapping
    print(f"[Masters] Loaded {len(mapping)} ledger mappings")
    return mapping

def get_mis_group(ledger_name: str, tally_native_group: str = '') -> tuple[str, str]:
    """
    Returns (tally_group, mis_group) for a ledger.
    Fallback: use tally_native_group if ledger not in Masters.
    """
    mapping = load_masters()
    if ledger_name in mapping:
        return mapping[ledger_name]['tally_group'], mapping[ledger_name]['mis_group']
    # Fallback — auto classify from Tally native group
    auto_mis = _auto_classify(tally_native_group or ledger_name)
    return tally_native_group, auto_mis

def _auto_classify(group_name: str) -> str:
    """
    Fallback classification based on Tally group names.
    Returns a sensible MIS Group label.
    """
    g = group_name.lower()
    if any(x in g for x in ['sales accounts', 'sales']):
        return 'Sales Accounts'
    if any(x in g for x in ['purchase accounts', 'purchase']):
        return 'Purchase Accounts'
    if 'direct expenses' in g or 'direct exp' in g:
        return 'Direct Expenses'
    if 'indirect expenses' in g or 'indirect exp' in g:
        return 'Indirect Expenses'
    if 'indirect income' in g or 'other income' in g:
        return 'Indirect Income'
    if 'opening stock' in g:
        return 'Opening Stock'
    if 'closing stock' in g:
        return 'Closing Stock'
    if any(x in g for x in ['sundry debtors', 'trade receivables']):
        return 'Sundry Debtors'
    if any(x in g for x in ['sundry creditors', 'trade payables']):
        return 'Sundry Creditors'
    if any(x in g for x in ['bank accounts', 'bank od']):
        return 'Bank Accounts'
    if 'cash' in g:
        return 'Cash-in-Hand'
    if any(x in g for x in ['loans', 'secured', 'unsecured']):
        return 'Loans'
    if any(x in g for x in ['fixed assets', 'plant', 'building', 'machinery']):
        return 'Fixed Assets'
    if 'capital' in g:
        return 'Capital Account'
    return group_name   # Return as-is if nothing matches
