"""
core/utils.py — Shared utility functions.

Centralises helpers previously duplicated across app.py, reports.py,
dashboard.py, downloads.py, and sync_engine.py.
"""
from __future__ import annotations
from datetime import date
from core.constants import MONTHS


# ── DATE / MONTH HELPERS ───────────────────────────────────────

def month_label(year: int, month: int) -> str:
    """Return a compact month label like 'Apr-24'."""
    return f"{MONTHS[month - 1]}-{str(year)[2:]}"


def build_mo_opts(rows) -> list[str]:
    """
    Convert DB rows (with 'year' and 'month' columns) into a sorted
    list of month-label strings, e.g. ['Apr-23', 'May-23', ...].

    Args:
        rows: Iterable of sqlite3.Row or dict with 'year' and 'month' keys.
    """
    return [
        month_label(int(r['year']), int(r['month']))
        for r in rows
    ]


def build_yr_mo_map(rows) -> dict[str, tuple[int, int]]:
    """
    Convert DB rows into a mapping: label → (year, month).
    E.g. {'Apr-23': (2023, 4), 'May-23': (2023, 5), ...}
    """
    return {
        month_label(int(r['year']), int(r['month'])): (int(r['year']), int(r['month']))
        for r in rows
    }


def get_fiscal_year(ref: date | None = None) -> tuple[date, date]:
    """
    Return (fy_start, fy_end) for the fiscal year containing `ref`.
    Indian FY: April 1 – March 31.
    """
    ref = ref or date.today()
    fy_start_year = ref.year if ref.month >= 4 else ref.year - 1
    return date(fy_start_year, 4, 1), date(fy_start_year + 1, 3, 31)


def get_last_fiscal_year(ref: date | None = None) -> tuple[date, date]:
    """Return (fy_start, fy_end) for the previous fiscal year."""
    ref = ref or date.today()
    fy_start_year = (ref.year - 1) if ref.month >= 4 else (ref.year - 2)
    return date(fy_start_year, 4, 1), date(fy_start_year + 1, 3, 31)


# ── NUMBER FORMATTING ──────────────────────────────────────────

def fmt_inr(value: float) -> str:
    """
    Format a rupee value with Indian short notation:
      ≥ 1 Cr  → ₹X.XXCr
      ≥ 1 L   → ₹X.XL
      else    → ₹X,XXX
    """
    a = abs(value)
    sign = '-' if value < 0 else ''
    if a >= 1e7:
        return f"{sign}₹{a / 1e7:.2f}Cr"
    if a >= 1e5:
        return f"{sign}₹{a / 1e5:.1f}L"
    return f"{sign}₹{a:,.0f}"


def fmt_inr_full(value: float) -> str:
    """Full rupee format with commas, e.g. ₹1,23,45,678."""
    return f"₹{abs(value):,.0f}" if value >= 0 else f"-₹{abs(value):,.0f}"
