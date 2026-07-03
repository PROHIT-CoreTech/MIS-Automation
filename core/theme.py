"""
core/theme.py — "Convix Light" design system for MIS Portal
Light, editorial fintech theme: soft neutral canvas (#ededed), white glass
cards, orange (#ef4d23) accent, near-black (#0b0f1a) CTAs, Inter for body
text, Instrument Serif italic for a single elegant accent word per headline.

Usage in app.py:
    from core.theme import inject_theme, inject_tilt_js, inject_sidebar_toggle
    inject_theme()            # call once, right after st.set_page_config
    inject_tilt_js()          # optional, only on the login page (3D tilt card)
    inject_sidebar_toggle()   # call once per page render — guaranteed sidebar
                               # show/hide button, independent of Streamlit's
                               # internal testid names (which change between
                               # versions and were the reason the old collapse
                               # arrow kept disappearing).
"""
import streamlit as st
import streamlit.components.v1 as components


def inject_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');

    :root {
        --bg:          #ededed;   /* page canvas */
        --tray:        #f5f2ee;   /* secondary surface / inputs */
        --surface:     #ffffff;   /* cards */
        --border:      rgba(11,15,26,0.08);
        --border-hi:   rgba(11,15,26,0.16);
        --orange:      #ef4d23;
        --orange-dim:  rgba(239,77,35,0.10);
        --dark:        #0b0f1a;   /* CTA / headings */
        --text-hi:     #0b0f1a;
        --text-mid:    #4b5563;
        --text-lo:     #8a8f98;
        --green:       #16a34a;
        --green-dim:   #f0fdf4;
        --red:         #dc2626;
        --red-dim:     #fef2f2;
    }

    /* ── BASE ─────────────────────────────────────────── */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    html, body { background: var(--bg) !important; }

    .stApp { background: var(--bg); color: var(--text-hi); }

    h1, h2, h3, h4 { font-family: 'Inter', sans-serif !important; letter-spacing: -0.02em; color: var(--text-hi); }
    p, span, label, div { color: var(--text-hi); }

    .accent-serif {
        font-family: 'Instrument Serif', serif;
        font-style: italic;
        font-weight: 400;
        color: var(--orange);
    }

    #MainMenu, footer { visibility: hidden; }
    div[data-testid="stSidebarNav"] { display: none; }

    header[data-testid="stHeader"] {
        background: var(--bg) !important;
        height: 2.2rem !important;
        box-shadow: none !important;
        border: none !important;
    }
    div[data-testid="stDecoration"] { display: none !important; }
    div[data-testid="stToolbar"] button[kind="header"] { visibility: hidden; }

    .block-container { padding-top: 0.9rem !important; }
    section[data-testid="stSidebar"] .block-container { padding-top: 0.4rem !important; }

    /* We render our own guaranteed toggle (inject_sidebar_toggle in
       core/theme.py) — hide Streamlit's native arrow entirely so there
       aren't two overlapping controls eating vertical space. */
    [data-testid="collapsedControl"] { display: none !important; }

    /* ── STICKY PAGE HEADER (title + company name) ─────
       Wrap these in <div class="page-sticky-header">...</div> right
       after the company name is known — stays visible while the user
       scrolls down through charts/tables. */
    .page-sticky-header {
        position: sticky;
        top: 0;
        z-index: 40;
        background: var(--bg);
        padding: 0.7rem 0 0.6rem 0;
        margin-bottom: 0.2rem;
    }
    .page-title-row {
        display: flex; align-items: center; gap: 8px;
        font-size: 1.5rem; font-weight: 700; color: var(--text-hi);
        letter-spacing: -0.02em; line-height: 1.35;
        padding-top: 2px;
    }
    .page-company-row {
        display: flex; align-items: center; gap: 6px;
        font-size: 0.95rem; font-weight: 600; color: var(--text-mid);
        margin-top: 2px;
    }

    /* ── SIDEBAR ──────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] * { color: var(--text-hi); }
    section[data-testid="stSidebar"] > div:first-child { padding-top: 0.5rem; }

    .mis-header {
        display: flex; align-items: center; gap: 8px;
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-hi);
        padding: 0.4rem 0 0.6rem 0;
        margin: 0;
        letter-spacing: -0.01em;
    }

    .user-block {
        background: var(--tray);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.65rem 0.85rem;
        margin: 0.4rem 0 0.7rem 0;
    }
    .user-name { font-weight: 600; font-size: 0.9rem; color: var(--text-hi); margin: 0; }
    .user-role {
        font-size: 0.7rem; color: var(--orange); margin: 2px 0 0 0;
        text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600;
    }

    /* ── BUTTONS ──────────────────────────────────────── */
    .stButton > button {
        background: var(--surface) !important;
        color: var(--text-hi) !important;
        border: 1px solid var(--border-hi) !important;
        border-radius: 999px !important;
        font-weight: 500 !important;
        transition: all 0.18s ease !important;
    }
    .stButton > button:hover {
        border-color: var(--orange) !important;
        background: var(--orange-dim) !important;
        color: var(--orange) !important;
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"] {
        background: var(--orange) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(239,77,35,0.28) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #d8431d !important;
        box-shadow: 0 6px 20px rgba(239,77,35,0.4) !important;
        transform: translateY(-2px);
    }

    /* ── INPUTS ───────────────────────────────────────── */
    .stTextInput > div, .stTextInput > div > div,
    .stSelectbox > div, .stSelectbox > div > div,
    .stDateInput > div, .stDateInput > div > div,
    div[data-baseweb="input"], div[data-baseweb="base-input"],
    div[data-baseweb="select"] > div {
        background-color: var(--tray) !important;
        border-color: var(--border-hi) !important;
    }
    .stTextInput input, .stDateInput input {
        background: var(--tray) !important;
        border: 1px solid var(--border-hi) !important;
        border-radius: 10px !important;
        color: var(--text-hi) !important;
        caret-color: var(--orange) !important;
    }
    .stTextInput input::placeholder { color: var(--text-lo) !important; opacity: 1; }
    .stTextInput input:focus, .stSelectbox > div > div:focus-within {
        border-color: var(--orange) !important;
        box-shadow: 0 0 0 3px var(--orange-dim) !important;
    }
    .stTextInput label, .stSelectbox label, .stDateInput label { color: var(--text-mid) !important; font-weight: 500; }
    .stSelectbox svg { fill: var(--text-mid) !important; }
    ul[data-baseweb="menu"], div[data-baseweb="popover"] div[role="listbox"] {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
    }
    li[role="option"] { color: var(--text-hi) !important; }
    li[role="option"]:hover, li[aria-selected="true"] { background-color: var(--orange-dim) !important; }

    /* ── GLASS / CONTENT CARD ─────────────────────────── */
    .glass-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        box-shadow: 0 1px 2px rgba(11,15,26,0.04);
        transition: all 0.2s ease;
    }
    .glass-card:hover {
        border-color: var(--border-hi);
        transform: translateY(-2px);
        box-shadow: 0 10px 28px rgba(11,15,26,0.08);
    }

    .chart-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1rem 1.1rem 0.4rem 1.1rem;
        box-shadow: 0 1px 2px rgba(11,15,26,0.04);
        margin-bottom: 1rem;
    }
    .chart-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.92rem;
        font-weight: 600;
        color: var(--text-hi);
        margin: 0 0 0.4rem 0;
    }

    /* ── DIVIDERS / MISC ──────────────────────────────── */
    hr { border-color: var(--border) !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background: var(--tray);
        border-radius: 10px 10px 0 0;
        color: var(--text-lo);
    }
    .stTabs [aria-selected="true"] {
        background: var(--orange-dim) !important;
        color: var(--orange) !important;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff 0%, #f4f5f7 100%);
        border: 1px solid rgba(11,15,26,0.06);
        border-radius: 18px;
        padding: 1.2rem 1.3rem;
        /* Layered shadow = real depth: soft ambient + directional drop
           + inner top highlight (the bevel) + inner bottom shade. */
        box-shadow:
            0 1px 1px rgba(11,15,26,0.04),
            0 8px 16px -6px rgba(11,15,26,0.12),
            0 18px 32px -12px rgba(11,15,26,0.10),
            inset 0 1px 0 rgba(255,255,255,0.9),
            inset 0 -2px 4px rgba(11,15,26,0.03);
        transition: transform 0.22s cubic-bezier(.2,.8,.2,1), box-shadow 0.22s ease;
        /* Equal height regardless of whether a trend/delta pill is present */
        min-height: 132px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow:
            0 2px 2px rgba(11,15,26,0.05),
            0 14px 24px -8px rgba(11,15,26,0.16),
            0 28px 48px -14px rgba(11,15,26,0.14),
            inset 0 1px 0 rgba(255,255,255,0.95),
            inset 0 -2px 4px rgba(11,15,26,0.03);
    }
    div[data-testid="stMetricLabel"] { color: var(--text-mid) !important; }
    div[data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: var(--text-hi) !important;
        font-variant-numeric: tabular-nums;
        font-size: clamp(1.05rem, 1.9vw, 1.7rem) !important;
        white-space: normal !important;
        overflow-wrap: break-word;
        line-height: 1.2 !important;
    }

    .badge-pill {
        display: inline-flex; align-items: center; gap: 8px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 6px 16px;
        font-size: 12px; font-weight: 600;
        color: var(--orange);
        letter-spacing: 0.04em;
        box-shadow: 0 1px 2px rgba(11,15,26,0.04);
    }
    .badge-pill .dot {
        width: 6px; height: 6px; border-radius: 50%;
        background: var(--orange);
    }

    /* ── FIXED GLOBAL LOGOUT (main area, top-right) ────────
       The button lives in a normal Streamlit container; we pin its
       keyed wrapper (.st-key-global_logout) to the top-right of the
       viewport so it floats above page content on every page,
       outside the sidebar. */
    .st-key-global_logout {
        position: fixed !important;
        top: 12px !important;
        right: 18px !important;
        z-index: 999998 !important;
        width: auto !important;
    }
    .st-key-global_logout button {
        background: var(--surface) !important;
        color: var(--orange) !important;
        border: 1px solid var(--orange) !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        padding: 0.3rem 1rem !important;
        box-shadow: 0 2px 8px rgba(11,15,26,0.12) !important;
    }
    .st-key-global_logout button:hover {
        background: var(--orange) !important;
        color: #ffffff !important;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)


def brand_mark(size=28):
    """Orange 8-petal flower mark — reusable inline SVG for MIS Portal's
    own brand icon (sidebar header, login badge)."""
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
      <g fill="#ef4d23">
        <circle cx="16" cy="16" r="3.5"/>
        <circle cx="16" cy="6"  r="3.5"/>
        <circle cx="16" cy="26" r="3.5"/>
        <circle cx="6"  cy="16" r="3.5"/>
        <circle cx="26" cy="16" r="3.5"/>
        <circle cx="9.1" cy="9.1"  r="3.5"/>
        <circle cx="22.9" cy="9.1"  r="3.5"/>
        <circle cx="9.1" cy="22.9" r="3.5"/>
        <circle cx="22.9" cy="22.9" r="3.5"/>
      </g>
    </svg>
    """


def inject_sidebar_toggle():
    """
    Guaranteed sidebar show/hide control, independent of Streamlit's
    internal element names (data-testid values shift between versions,
    which is why the native collapse arrow kept vanishing).

    Renders one fixed, always-visible orange-bordered button top-left.
    Clicking it finds whichever native Streamlit toggle exists in the
    DOM (tries several known selectors across versions) and clicks it —
    piggybacking on Streamlit's real toggle logic instead of
    reimplementing layout state.
    """
    components.html("""
    <script>
    (function() {
        const doc = window.parent.document;
        function ensureButton() {
            if (doc.getElementById('mis-sb-toggle')) return;
            const btn = doc.createElement('button');
            btn.id = 'mis-sb-toggle';
            btn.innerHTML = '&#9776;';
            btn.title = 'Show / hide sidebar';
            Object.assign(btn.style, {
                position: 'fixed', top: '10px', left: '10px', zIndex: 999999,
                width: '34px', height: '34px', borderRadius: '8px',
                background: '#ffffff', border: '1px solid #ef4d23',
                color: '#ef4d23', fontSize: '16px', cursor: 'pointer',
                boxShadow: '0 2px 8px rgba(11,15,26,0.15)'
            });
            btn.addEventListener('click', function() {
                const selectors = [
                    '[data-testid="collapsedControl"]',
                    '[data-testid="stSidebarCollapseButton"] button',
                    'button[data-testid="baseButton-headerNoPadding"]',
                    'section[data-testid="stSidebar"] button[kind="header"]',
                ];
                for (const sel of selectors) {
                    const el = doc.querySelector(sel);
                    if (el) { el.click(); return; }
                }
            });
            doc.body.appendChild(btn);
        }
        ensureButton();
        let tries = 0;
        const iv = setInterval(() => { ensureButton(); if (++tries > 20) clearInterval(iv); }, 300);
    })();
    </script>
    """, height=0, width=0)


# ── PLOTLY LIGHT TEMPLATE ────────────────────────────────────
CHART_COLORS = {
    'mint':   '#ef4d23',
    'blue':   '#0b0f1a',
    'violet': '#2E9BE7',
    'amber':  '#f59e0b',
    'red':    '#dc2626',
    'text':   '#4b5563',
    'text_hi':'#0b0f1a',
    'grid':   'rgba(11,15,26,0.06)',
}

CHART_PALETTE = ['#ef4d23', '#0b0f1a', '#2E9BE7', '#16a34a',
                  '#f59e0b', '#6c5ce7', '#dc2626', '#14b8a6']


def chart_layout(fig, **overrides):
    """Apply the standard light/card layout to any Plotly figure in place."""
    base = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=CHART_COLORS['text'], family='Inter, sans-serif', size=11),
        legend=dict(font=dict(color=CHART_COLORS['text'], size=10),
                    bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(showgrid=False, color=CHART_COLORS['text'],
                    linecolor='rgba(11,15,26,0.10)'),
        yaxis=dict(gridcolor=CHART_COLORS['grid'], color=CHART_COLORS['text'],
                    zerolinecolor='rgba(11,15,26,0.10)'),
        hoverlabel=dict(bgcolor='#ffffff', font_color=CHART_COLORS['text_hi'],
                         bordercolor='rgba(11,15,26,0.1)'),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    base.update(overrides)
    fig.update_layout(**base)
    return fig


def donut_chart_figure(labels, values, palette=None, center_text=None):
    """Donut chart with a soft drop-shadow layer for a lifted/embossed
    feel on a light card background."""
    import plotly.graph_objects as go
    palette = palette or CHART_PALETTE
    colors = [palette[i % len(palette)] for i in range(len(labels))]

    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels, values=values, hole=0.6, sort=False,
        marker=dict(colors=['rgba(11,15,26,0.10)'] * len(labels)),
        textinfo='none', hoverinfo='skip', showlegend=False,
        domain=dict(x=[0.015, 1.0], y=[0.0, 0.985]),
    ))
    fig.add_trace(go.Pie(
        labels=labels, values=values, hole=0.6, sort=False,
        marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
        textinfo='percent', textfont=dict(color='#ffffff', size=10, family='Inter'),
        hovertemplate='%{label}: ₹%{value:,.0f}<extra></extra>',
        domain=dict(x=[0.0, 0.985], y=[0.015, 1.0]),
    ))
    total = sum(values) if values else 0
    if center_text is None:
        a = abs(total)
        center_text = f"₹{a/1e7:.2f}Cr" if a >= 1e7 else f"₹{a/1e5:.1f}L" if a >= 1e5 else f"₹{a:,.0f}"
    chart_layout(fig, showlegend=True,
                 legend=dict(orientation='v', x=1.0, y=0.5,
                             font=dict(color=CHART_COLORS['text'], size=10)),
                 annotations=[dict(text=center_text, x=0.49, y=0.5, showarrow=False,
                                    font=dict(size=15, color=CHART_COLORS['text_hi'],
                                               family='Inter'))])
    return fig


def inject_tilt_js():
    """Mouse-tracking 3D tilt for the element with class 'tilt-card'."""
    components.html("""
    <script>
    (function() {
        const doc = window.parent.document;
        function attach() {
            const card = doc.querySelector('.tilt-card');
            if (!card || card.dataset.tiltBound) return;
            card.dataset.tiltBound = "1";
            card.style.transition = "transform 0.15s ease-out";
            card.style.transformStyle = "preserve-3d";
            card.addEventListener('mousemove', (e) => {
                const r = card.getBoundingClientRect();
                const x = (e.clientX - r.left) / r.width  - 0.5;
                const y = (e.clientY - r.top)  / r.height - 0.5;
                const rx = (-y * 4).toFixed(2);
                const ry = ( x * 4).toFixed(2);
                card.style.transform =
                    `perspective(1000px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-4px)`;
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = "perspective(1000px) rotateX(0) rotateY(0) translateY(0)";
            });
        }
        attach();
        let tries = 0;
        const iv = setInterval(() => { attach(); tries++; if (tries > 20) clearInterval(iv); }, 250);
    })();
    </script>
    """, height=0, width=0)
