"""
core/theme/__init__.py — Public API for the theme sub-package.

Re-exports all symbols that external modules import from `core.theme`,
ensuring zero breaking changes when callers do:
    from core.theme import inject_theme, chart_layout, CHART_COLORS, ...
"""
from core.theme.styles     import inject_theme, inject_sidebar_toggle, inject_tilt_js
from core.theme.charts     import chart_layout, donut_chart_figure, CHART_COLORS, CHART_PALETTE
from core.theme.components import brand_mark

__all__ = [
    # Styles
    'inject_theme',
    'inject_sidebar_toggle',
    'inject_tilt_js',
    # Charts
    'chart_layout',
    'donut_chart_figure',
    'CHART_COLORS',
    'CHART_PALETTE',
    # Components
    'brand_mark',
]
