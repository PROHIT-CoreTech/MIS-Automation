"""
core/theme/charts.py — Plotly chart helpers for the MIS Portal dark theme.

Extracted from core/theme.py (monolith).
Contains: CHART_COLORS, CHART_PALETTE, chart_layout(), donut_chart_figure()
"""
import plotly.graph_objects as go

# ── COLOR SYSTEM ───────────────────────────────────────────────
CHART_COLORS: dict = {
    'accent':  '#6366f1',
    'orange':  '#f97316',
    'emerald': '#10b981',
    'sky':     '#38bdf8',
    'amber':   '#fbbf24',
    'rose':    '#f43f5e',
    'violet':  '#a78bfa',
    'text':    '#94a3b8',
    'text_hi': '#f1f5f9',
    'grid':    'rgba(255,255,255,0.05)',
    # Backward-compat aliases
    'mint':    '#6366f1',
    'blue':    '#38bdf8',
    'red':     '#f43f5e',
}

CHART_PALETTE: list = [
    '#6366f1', '#f97316', '#10b981', '#38bdf8',
    '#fbbf24', '#a78bfa', '#f43f5e', '#2dd4bf',
]


def chart_layout(fig: go.Figure, **overrides) -> go.Figure:
    """Apply the premium dark Plotly layout to any figure in-place and return it."""
    base = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=CHART_COLORS['text'], family='Inter, sans-serif', size=11),
        legend=dict(
            font=dict(color=CHART_COLORS['text'], size=10),
            bgcolor='rgba(0,0,0,0)',
        ),
        xaxis=dict(
            showgrid=False,
            color=CHART_COLORS['text'],
            linecolor='rgba(255,255,255,0.08)',
            tickfont=dict(color=CHART_COLORS['text']),
        ),
        yaxis=dict(
            gridcolor=CHART_COLORS['grid'],
            color=CHART_COLORS['text'],
            zerolinecolor='rgba(255,255,255,0.08)',
            tickfont=dict(color=CHART_COLORS['text']),
        ),
        hoverlabel=dict(
            bgcolor='rgba(15,22,41,0.95)',
            font_color=CHART_COLORS['text_hi'],
            bordercolor='rgba(99,102,241,0.4)',
            font=dict(family='Inter, sans-serif'),
        ),
        margin=dict(l=12, r=12, t=12, b=12),
    )
    base.update(overrides)
    fig.update_layout(**base)
    return fig


def donut_chart_figure(
    labels: list,
    values: list,
    palette: list | None = None,
    center_text: str | None = None,
) -> go.Figure:
    """
    Dark-mode donut chart with inner glow shadow layer.

    Args:
        labels:      Slice labels.
        values:      Slice values (numeric).
        palette:     Optional color list; defaults to CHART_PALETTE.
        center_text: Text to display in the donut hole. Auto-formats in INR if None.
    """
    palette = palette or CHART_PALETTE
    colors = [palette[i % len(palette)] for i in range(len(labels))]

    fig = go.Figure()

    # Shadow layer (subtle glow behind slices)
    fig.add_trace(go.Pie(
        labels=labels, values=values, hole=0.6, sort=False,
        marker=dict(colors=['rgba(99,102,241,0.08)'] * len(labels)),
        textinfo='none', hoverinfo='skip', showlegend=False,
        domain=dict(x=[0.015, 1.0], y=[0.0, 0.985]),
    ))

    # Main data layer
    fig.add_trace(go.Pie(
        labels=labels, values=values, hole=0.6, sort=False,
        marker=dict(
            colors=colors,
            line=dict(color='rgba(8,12,22,0.8)', width=2),
        ),
        textinfo='percent',
        textfont=dict(color='#ffffff', size=10, family='Inter'),
        hovertemplate='%{label}: ₹%{value:,.0f}<extra></extra>',
        domain=dict(x=[0.0, 0.985], y=[0.015, 1.0]),
    ))

    total = sum(values) if values else 0
    if center_text is None:
        a = abs(total)
        center_text = (
            f"₹{a / 1e7:.2f}Cr" if a >= 1e7
            else f"₹{a / 1e5:.1f}L" if a >= 1e5
            else f"₹{a:,.0f}"
        )

    chart_layout(
        fig,
        showlegend=True,
        legend=dict(orientation='v', x=1.0, y=0.5,
                    font=dict(color=CHART_COLORS['text'], size=10)),
        annotations=[dict(
            text=center_text, x=0.49, y=0.5, showarrow=False,
            font=dict(size=15, color=CHART_COLORS['text_hi'],
                      family='Inter, sans-serif', weight=700),
        )],
    )
    return fig
