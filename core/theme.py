"""
core/theme.py — "Convix Dark" premium design system for MIS Portal
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deep navy dark theme with glassmorphism, gradient accents, glowing
KPI cards, animated sidebar nav pills, and premium Inter typography.

Design tokens:
  --bg-base    : #080c16   deep space navy (canvas)
  --bg-surface : #0f1629   slightly lighter (panels)
  --glass      : rgba(15,22,41,0.7) + blur — glassmorphism cards
  --border     : rgba(255,255,255,0.07)
  --accent     : #6366f1   indigo (primary)
  --orange     : #f97316   amber-orange (highlights)
  --emerald    : #10b981   profit green
  --rose       : #f43f5e   loss red
  --text-hi    : #f1f5f9   near-white
  --text-mid   : #94a3b8   slate-400
  --text-lo    : #475569   slate-600
"""
import streamlit as st
import streamlit.components.v1 as components


def inject_theme():
    st.markdown("""
    <style>
    /* ── FONTS ─────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── DESIGN TOKENS ─────────────────────────────────────── */
    :root {
        --bg-base:     #080c16;
        --bg-surface:  #0f1629;
        --bg-elevated: #141c35;
        --glass:       rgba(15, 22, 41, 0.72);
        --glass-hi:    rgba(255, 255, 255, 0.04);
        --border:      rgba(255, 255, 255, 0.07);
        --border-hi:   rgba(255, 255, 255, 0.14);
        --border-glow: rgba(99, 102, 241, 0.40);

        --accent:      #6366f1;   /* indigo */
        --accent-dim:  rgba(99, 102, 241, 0.15);
        --accent-glow: rgba(99, 102, 241, 0.35);
        --orange:      #f97316;   /* amber */
        --orange-dim:  rgba(249, 115, 22, 0.14);
        --orange-glow: rgba(249, 115, 22, 0.35);
        --emerald:     #10b981;
        --emerald-dim: rgba(16, 185, 129, 0.14);
        --rose:        #f43f5e;
        --rose-dim:    rgba(244, 63, 94, 0.14);
        --sky:         #38bdf8;
        --amber:       #fbbf24;

        --text-hi:     #f1f5f9;
        --text-mid:    #94a3b8;
        --text-lo:     #475569;

        --radius-sm:   10px;
        --radius-md:   16px;
        --radius-lg:   24px;
        --radius-xl:   32px;
    }

    /* ── ANIMATED MESH GRADIENT BACKGROUND ─────────────────── */
    @keyframes meshShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 0 0 var(--accent-glow); }
        50%       { box-shadow: 0 0 20px 4px var(--accent-glow); }
    }
    @keyframes shimmer {
        0%   { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    @keyframes dot-pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50%       { transform: scale(1.4); opacity: 0.7; }
    }

    /* ── RESET / BASE ──────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    html, body {
        background: var(--bg-base) !important;
        color: var(--text-hi) !important;
    }
    .stApp {
        background:
            radial-gradient(ellipse 80% 60% at 20% 0%,  rgba(99,102,241,0.12) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 80% 100%, rgba(249,115,22,0.08) 0%, transparent 55%),
            radial-gradient(ellipse 50% 40% at 50% 50%,  rgba(16,185,129,0.05) 0%, transparent 60%),
            var(--bg-base) !important;
        color: var(--text-hi);
        animation: fadeIn 0.4s ease;
    }

    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        color: var(--text-hi) !important;
    }
    p, span, label, div { color: var(--text-hi); }

    .accent-serif {
        font-family: 'Instrument Serif', serif;
        font-style: italic;
        font-weight: 400;
        background: linear-gradient(135deg, var(--accent), var(--orange));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ── SCROLLBAR ─────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 99px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

    /* ── HIDE STREAMLIT CHROME ─────────────────────────────── */
    #MainMenu, footer { visibility: hidden; }
    div[data-testid="stSidebarNav"] { display: none; }
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 2.2rem !important;
        box-shadow: none !important;
        border: none !important;
    }
    div[data-testid="stDecoration"] { display: none !important; }
    div[data-testid="stToolbar"] button[kind="header"] { visibility: hidden; }
    [data-testid="collapsedControl"] { display: none !important; }

    .block-container { padding-top: 0.9rem !important; }
    section[data-testid="stSidebar"] .block-container { padding-top: 0.4rem !important; }

    /* ── STICKY PAGE HEADER ────────────────────────────────── */
    .page-sticky-header {
        position: sticky; top: 0; z-index: 40;
        background: linear-gradient(180deg, var(--bg-base) 60%, transparent 100%);
        padding: 0.7rem 0 0.6rem 0;
        margin-bottom: 0.3rem;
        backdrop-filter: blur(8px);
    }
    .page-title-row {
        display: flex; align-items: center; gap: 10px;
        font-size: 1.55rem; font-weight: 800; color: var(--text-hi);
        letter-spacing: -0.04em; line-height: 1.25;
    }
    .page-company-row {
        display: flex; align-items: center; gap: 6px;
        font-size: 0.88rem; font-weight: 500; color: var(--text-mid);
        margin-top: 3px;
    }

    /* ── SIDEBAR ───────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(99,102,241,0.08) 0%, transparent 40%),
            var(--bg-surface) !important;
        border-right: 1px solid var(--border) !important;
        backdrop-filter: blur(20px);
    }
    section[data-testid="stSidebar"] * { color: var(--text-hi); }
    section[data-testid="stSidebar"] > div:first-child { padding-top: 0.5rem; }

    .mis-header {
        display: flex; align-items: center; gap: 8px;
        font-size: 1.08rem; font-weight: 800; color: var(--text-hi);
        padding: 0.5rem 0 0.7rem 0; margin: 0;
        letter-spacing: -0.03em;
    }

    .user-block {
        background: var(--glass-hi);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 0.7rem 0.9rem;
        margin: 0.4rem 0 0.8rem 0;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    .user-block::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent), transparent);
    }
    .user-name { font-weight: 600; font-size: 0.88rem; color: var(--text-hi); margin: 0; }
    .user-role {
        font-size: 0.68rem; color: var(--accent); margin: 3px 0 0 0;
        text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700;
    }

    /* ── BUTTONS ───────────────────────────────────────────── */
    .stButton > button {
        background: var(--glass-hi) !important;
        color: var(--text-mid) !important;
        border: 1px solid var(--border-hi) !important;
        border-radius: 999px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.2s cubic-bezier(.2,.8,.2,1) !important;
        backdrop-filter: blur(8px) !important;
    }
    .stButton > button:hover {
        border-color: var(--accent) !important;
        background: var(--accent-dim) !important;
        color: var(--accent) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 16px var(--accent-glow) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent) 0%, #818cf8 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 4px 20px var(--accent-glow) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4f52d9 0%, #6366f1 100%) !important;
        box-shadow: 0 8px 28px var(--accent-glow) !important;
        transform: translateY(-2px) !important;
    }

    /* ── INPUTS ────────────────────────────────────────────── */
    .stTextInput > div, .stTextInput > div > div,
    .stSelectbox > div, .stSelectbox > div > div,
    div[data-baseweb="input"], div[data-baseweb="base-input"],
    div[data-baseweb="select"] > div {
        background-color: var(--bg-elevated) !important;
        border-color: var(--border-hi) !important;
    }
    .stTextInput input, .stDateInput input {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-hi) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-hi) !important;
        caret-color: var(--accent) !important;
    }
    .stTextInput input::placeholder { color: var(--text-lo) !important; opacity: 1; }
    .stTextInput input:focus, .stSelectbox > div > div:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-dim) !important;
    }
    .stTextInput label, .stSelectbox label, .stDateInput label {
        color: var(--text-mid) !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.03em !important;
        text-transform: uppercase !important;
    }
    .stSelectbox svg { fill: var(--text-mid) !important; }
    ul[data-baseweb="menu"], div[data-baseweb="popover"] div[role="listbox"] {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border-hi) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: 0 24px 48px rgba(0,0,0,0.5) !important;
    }
    li[role="option"] { color: var(--text-hi) !important; }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: var(--accent-dim) !important;
        color: var(--accent) !important;
    }

    /* ── METRIC KPI CARDS ──────────────────────────────────── */
    div[data-testid="stMetric"] {
        background:
            linear-gradient(145deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%),
            var(--glass) !important;
        border: 1px solid var(--border-hi) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.3rem 1.4rem !important;
        backdrop-filter: blur(20px) !important;
        box-shadow:
            0 1px 0 rgba(255,255,255,0.06) inset,
            0 8px 32px rgba(0,0,0,0.35),
            0 1px 2px rgba(0,0,0,0.3) !important;
        transition: all 0.25s cubic-bezier(.2,.8,.2,1) !important;
        position: relative !important;
        overflow: hidden !important;
        min-height: 128px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, var(--accent), var(--orange), var(--emerald));
        opacity: 0;
        transition: opacity 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px) !important;
        border-color: var(--border-glow) !important;
        box-shadow:
            0 1px 0 rgba(255,255,255,0.08) inset,
            0 16px 40px rgba(0,0,0,0.45),
            0 0 0 1px var(--accent-glow) !important;
    }
    div[data-testid="stMetric"]:hover::before { opacity: 1; }

    div[data-testid="stMetricLabel"] {
        color: var(--text-mid) !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        color: var(--text-hi) !important;
        font-variant-numeric: tabular-nums !important;
        font-size: clamp(1.1rem, 2vw, 1.75rem) !important;
        letter-spacing: -0.02em !important;
        white-space: normal !important;
        line-height: 1.15 !important;
    }
    div[data-testid="stMetricDelta"] svg { display: none !important; }
    div[data-testid="stMetricDelta"] > div {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        padding: 2px 8px;
        border-radius: 99px;
        display: inline-block;
    }

    /* ── GLASS / CHART CARDS ───────────────────────────────── */
    .glass-card {
        background: var(--glass);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        backdrop-filter: blur(16px);
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
        transition: all 0.22s ease;
    }
    .glass-card:hover {
        border-color: var(--border-glow);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4), 0 0 0 1px var(--accent-glow);
    }

    .chart-card {
        background:
            linear-gradient(145deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.005) 100%),
            var(--glass);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.1rem 1.2rem 0.5rem 1.2rem;
        backdrop-filter: blur(16px);
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    .chart-card::after {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    }
    .chart-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--text-hi);
        margin: 0 0 0.5rem 0;
        letter-spacing: 0.01em;
    }

    /* ── TABS ──────────────────────────────────────────────── */
    /* Remove the congested pill-container box entirely */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
        background: transparent !important;
        border-radius: 0 !important;
        padding: 0 !important;
        border: none !important;
        border-bottom: 1px solid var(--border) !important;
        margin-bottom: 1.2rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        color: var(--text-lo) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        letter-spacing: 0.01em !important;
        padding: 0.7rem 1.4rem !important;
        margin: 0 !important;
        position: relative !important;
        transition: color 0.18s ease !important;
        white-space: nowrap !important;
        cursor: pointer !important;
        /* underline indicator */
        border-bottom: 2px solid transparent !important;
        margin-bottom: -1px !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-hi) !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: var(--accent) !important;
        font-weight: 700 !important;
        border-bottom: 2px solid var(--accent) !important;
        box-shadow: none !important;
    }
    /* Hide the default selection highlight bar Streamlit injects */
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* ── DIVIDERS ──────────────────────────────────────────── */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--border-hi), transparent) !important;
        margin: 1rem 0 !important;
    }

    /* ── ALERTS / INFO BOXES ───────────────────────────────── */
    div[data-testid="stAlert"] {
        background: var(--glass) !important;
        border: 1px solid var(--border-hi) !important;
        border-radius: var(--radius-md) !important;
        backdrop-filter: blur(10px) !important;
    }

    /* ── BADGE PILL ────────────────────────────────────────── */
    .badge-pill {
        display: inline-flex; align-items: center; gap: 8px;
        background: var(--glass);
        border: 1px solid var(--border-hi);
        border-radius: 999px;
        padding: 6px 18px;
        font-size: 11px; font-weight: 700;
        color: var(--accent);
        letter-spacing: 0.10em;
        text-transform: uppercase;
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 12px rgba(99,102,241,0.2);
    }
    .badge-pill .dot {
        width: 7px; height: 7px; border-radius: 50%;
        background: var(--accent);
        animation: dot-pulse 2s ease-in-out infinite;
        box-shadow: 0 0 6px var(--accent);
    }

    /* ── FIXED GLOBAL LOGOUT ───────────────────────────────── */
    .st-key-global_logout {
        position: fixed !important; top: 12px !important;
        right: 18px !important; z-index: 999998 !important;
        width: auto !important;
    }
    .st-key-global_logout button {
        background: var(--glass) !important;
        color: var(--rose) !important;
        border: 1px solid rgba(244, 63, 94, 0.35) !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        padding: 0.3rem 1rem !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 2px 12px rgba(244,63,94,0.2) !important;
        transition: all 0.2s ease !important;
    }
    .st-key-global_logout button:hover {
        background: var(--rose-dim) !important;
        box-shadow: 0 4px 20px rgba(244,63,94,0.4) !important;
        transform: translateY(-1px) !important;
    }
    </style>
    """, unsafe_allow_html=True)


def brand_mark(size=28):
    """Premium gradient brand mark — multi-node radial pattern for MIS Portal."""
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="bm" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%"   stop-color="#6366f1"/>
          <stop offset="100%" stop-color="#f97316"/>
        </linearGradient>
      </defs>
      <g fill="url(#bm)">
        <circle cx="16" cy="16" r="3.8"/>
        <circle cx="16" cy="5.5"  r="3"/>
        <circle cx="16" cy="26.5" r="3"/>
        <circle cx="5.5"  cy="16" r="3"/>
        <circle cx="26.5" cy="16" r="3"/>
        <circle cx="9"  cy="9"   r="2.6"/>
        <circle cx="23" cy="9"   r="2.6"/>
        <circle cx="9"  cy="23"  r="2.6"/>
        <circle cx="23" cy="23"  r="2.6"/>
      </g>
    </svg>
    """


def inject_sidebar_toggle():
    """
    Guaranteed sidebar show/hide control with premium dark styling.
    Renders a fixed top-left glass button that piggybacks on Streamlit's
    own toggle logic — independent of testid names across versions.
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
                width: '34px', height: '34px', borderRadius: '10px',
                background: 'rgba(15,22,41,0.8)',
                border: '1px solid rgba(99,102,241,0.4)',
                color: '#6366f1', fontSize: '15px', cursor: 'pointer',
                backdropFilter: 'blur(12px)',
                boxShadow: '0 4px 16px rgba(99,102,241,0.25)',
                transition: 'all 0.2s ease',
            });
            btn.onmouseover = () => {
                btn.style.background = 'rgba(99,102,241,0.2)';
                btn.style.boxShadow = '0 4px 20px rgba(99,102,241,0.45)';
                btn.style.transform = 'translateY(-1px)';
            };
            btn.onmouseout = () => {
                btn.style.background = 'rgba(15,22,41,0.8)';
                btn.style.boxShadow = '0 4px 16px rgba(99,102,241,0.25)';
                btn.style.transform = 'translateY(0)';
            };
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


# ── DARK PLOTLY CHART TEMPLATE ────────────────────────────────
CHART_COLORS = {
    'accent':   '#6366f1',
    'orange':   '#f97316',
    'emerald':  '#10b981',
    'sky':      '#38bdf8',
    'amber':    '#fbbf24',
    'rose':     '#f43f5e',
    'violet':   '#a78bfa',
    'text':     '#94a3b8',
    'text_hi':  '#f1f5f9',
    'grid':     'rgba(255,255,255,0.05)',
    'mint':     '#6366f1',   # kept for backward-compat alias
    'blue':     '#38bdf8',   # kept for backward-compat alias
    'red':      '#f43f5e',   # kept for backward-compat alias
}

CHART_PALETTE = [
    '#6366f1', '#f97316', '#10b981', '#38bdf8',
    '#fbbf24', '#a78bfa', '#f43f5e', '#2dd4bf',
]


def chart_layout(fig, **overrides):
    """Apply the premium dark layout to any Plotly figure in place."""
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


def donut_chart_figure(labels, values, palette=None, center_text=None):
    """Dark-mode donut chart with inner glow shadow layer."""
    import plotly.graph_objects as go
    palette = palette or CHART_PALETTE
    colors = [palette[i % len(palette)] for i in range(len(labels))]

    fig = go.Figure()
    # Shadow layer
    fig.add_trace(go.Pie(
        labels=labels, values=values, hole=0.6, sort=False,
        marker=dict(colors=['rgba(99,102,241,0.08)'] * len(labels)),
        textinfo='none', hoverinfo='skip', showlegend=False,
        domain=dict(x=[0.015, 1.0], y=[0.0, 0.985]),
    ))
    # Main layer
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
        center_text = (f"₹{a/1e7:.2f}Cr" if a >= 1e7
                       else f"₹{a/1e5:.1f}L" if a >= 1e5
                       else f"₹{a:,.0f}")

    chart_layout(fig, showlegend=True,
                 legend=dict(orientation='v', x=1.0, y=0.5,
                             font=dict(color=CHART_COLORS['text'], size=10)),
                 annotations=[dict(
                     text=center_text, x=0.49, y=0.5, showarrow=False,
                     font=dict(size=15, color=CHART_COLORS['text_hi'],
                               family='Inter, sans-serif', weight=700),
                 )])
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
            card.style.transition = "transform 0.12s ease-out, box-shadow 0.12s ease-out";
            card.style.transformStyle = "preserve-3d";
            card.addEventListener('mousemove', (e) => {
                const r = card.getBoundingClientRect();
                const x = (e.clientX - r.left) / r.width  - 0.5;
                const y = (e.clientY - r.top)  / r.height - 0.5;
                const rx = (-y * 6).toFixed(2);
                const ry = ( x * 6).toFixed(2);
                card.style.transform =
                    `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-6px)`;
                card.style.boxShadow =
                    `0 32px 64px rgba(99,102,241,0.25), 0 0 0 1px rgba(99,102,241,0.2)`;
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = "perspective(900px) rotateX(0) rotateY(0) translateY(0)";
                card.style.boxShadow = "";
            });
        }
        attach();
        let tries = 0;
        const iv = setInterval(() => { attach(); tries++; if (tries > 20) clearInterval(iv); }, 250);
    })();
    </script>
    """, height=0, width=0)
