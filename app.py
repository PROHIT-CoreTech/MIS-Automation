"""
MIS Portal — Main Entry Point
Run: python -m streamlit run app.py
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.db    import init_db
from core.auth  import create_admin_if_not_exists, login
from core.theme import inject_theme, inject_tilt_js, inject_sidebar_toggle, brand_mark

# ── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="MIS Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL THEME ("Convix Light" — editorial fintech) ──────
inject_theme()

# ── INIT DB ────────────────────────────────────────────────
@st.cache_resource
def initialize():
    init_db()
    create_admin_if_not_exists()
    return True

initialize()

# ── SESSION STATE ──────────────────────────────────────────
if 'user'          not in st.session_state: st.session_state.user          = None
if 'impersonating' not in st.session_state: st.session_state.impersonating = None
if 'page'          not in st.session_state: st.session_state.page          = 'dashboard'


# ── LOGIN PAGE ─────────────────────────────────────────────
def show_login():
    # Hide sidebar entirely on login screen
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] { display: none; }
        .block-container { padding-top: 4vh; max-width: 100%; }

        .login-title {
            font-size: clamp(32px, 6vw, 44px);
            font-weight: 600;
            letter-spacing: -0.02em;
            line-height: 1.08;
            color: #0b0f1a;
            margin: 18px 0 6px 0;
        }
        .login-sub {
            color: #4b5563;
            font-size: 0.95rem;
            margin: 0 0 28px 0;
        }

        /* The card wrapping the actual Streamlit form — white, rounded,
           soft shadow, matches the light Convix design language */
        div[data-testid="stForm"] {
            background: #ffffff !important;
            border: 1px solid rgba(11,15,26,0.08) !important;
            border-radius: 24px !important;
            padding: 2rem 2rem 1.4rem 2rem !important;
            box-shadow: 0 20px 48px rgba(11,15,26,0.10);
            position: relative;
            z-index: 1;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.15, 1])
    with col2:
        st.markdown(f"""
            <div style='text-align:center; position:relative; z-index:1;'>
                <div class="badge-pill"><span class="dot"></span>MIS PORTAL &middot; SECURE ACCESS</div>
                <h1 class="login-title">Welcome <span class="accent-serif">back</span></h1>
                <p class="login-sub">Sign in to view your live financial dashboard</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="tilt-card">', unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password",
                                     placeholder="Enter password")
            submit   = st.form_submit_button("Sign In →",
                                             use_container_width=True,
                                             type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

        if submit:
            if not username or not password:
                st.error("Please enter username and password")
            else:
                try:
                    user = login(username.strip(), password)
                    if user:
                        st.session_state.user = user
                        st.session_state.page = 'dashboard'
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                except PermissionError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Login error: {e}")

    inject_tilt_js()


# ── MAIN APP ───────────────────────────────────────────────
def show_app():
    user = st.session_state.impersonating or st.session_state.user
    real = st.session_state.user
    role = real.get('role')

    # Guaranteed sidebar show/hide button — works regardless of which
    # Streamlit version's internal testid names are in play.
    inject_sidebar_toggle()

    # ── FIXED LOGOUT (main area, top-right) — shows on every page ──
    # Rendered before page routing so it's always present. CSS pins the
    # button (targeted via its .st-key-global_logout wrapper) to the
    # top-right of the viewport, outside the sidebar.
    if st.button("🚪 Logout", key="global_logout"):
        st.session_state.user          = None
        st.session_state.impersonating = None
        st.session_state.page          = 'dashboard'
        st.rerun()

    # ── SIDEBAR ────────────────────────────────────────────
    with st.sidebar:
        # 1. MIS Portal title
        st.markdown(
            f'<p class="mis-header">{brand_mark(22)} MIS Portal</p>',
            unsafe_allow_html=True)

        # 2. User info block
        name = real.get('full_name') or real.get('username', '')
        st.markdown(f"""
            <div class="user-block">
                <p class="user-name">👤 {name}</p>
                <p class="user-role">{role.upper()}</p>
            </div>
        """, unsafe_allow_html=True)

        # 3. Navigation
        st.markdown("**Navigation**")
        nav_items = [
            ("📊 Dashboard",   "dashboard"),
            ("📄 MIS Reports", "reports"),
        ]
        if role == 'admin':
            nav_items += [
                ("⚙️ Admin Panel", "admin"),
                ("🔄 Sync Status", "sync"),
            ]

        for label, key in nav_items:
            is_active = st.session_state.page == key
            if st.button(label, key=f"nav_{key}",
                         use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.page = key
                st.rerun()

        # 4. Impersonation banner
        if st.session_state.impersonating:
            st.warning(f"👁 Viewing as:\n**{user.get('username')}**")
            if st.button("↩️ Exit View", use_container_width=True):
                st.session_state.impersonating = None
                st.session_state.page = 'dashboard'
                st.rerun()

    # ── PAGE ROUTING ───────────────────────────────────────
    # Note: dashboard.py and reports.py inject Company+Date Range
    # into sidebar via st.sidebar — Streamlit allows this after
    # the main sidebar block, and it appears at the insertion point
    page = st.session_state.page
    if page == 'dashboard':
        from portal_pages.dashboard import show_dashboard
        show_dashboard(user)
    elif page == 'reports':
        from portal_pages.reports import show_reports
        show_reports(user)
    elif page == 'admin':
        if role == 'admin':
            from portal_pages.admin import show_admin
            show_admin(real)
        else:
            st.error("⛔ Access denied")
    elif page == 'sync':
        if role == 'admin':
            from portal_pages.sync_status import show_sync
            show_sync(real)
        else:
            st.error("⛔ Access denied")


# ── ROUTER ─────────────────────────────────────────────────
if st.session_state.user is None:
    show_login()
else:
    show_app()
