"""
MIS Portal — Main Entry Point
Run: streamlit run app.py

Responsibilities:
  1. Page config + global theme
  2. One-time DB + admin initialisation (cached)
  3. Session state bootstrap
  4. Top-level router (login vs. app)

All UI logic is delegated to dedicated modules:
  - portal_pages.login   → show_login()
  - portal_pages.sidebar → show_sidebar()
  - portal_pages.*       → individual page renderers
"""
import logging
import streamlit as st

from core.db    import init_db
from core.auth  import create_admin_if_not_exists
from core.theme import inject_theme, inject_sidebar_toggle

# ── LOGGING ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)

# ── PAGE CONFIG ────────────────────────────────────────────────
st.set_page_config(
    page_title="MIS Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL THEME ───────────────────────────────────────────────
inject_theme()


# ── ONE-TIME INITIALISATION ────────────────────────────────────
@st.cache_resource
def _initialize():
    init_db()
    create_admin_if_not_exists()
    return True


_initialize()


# ── SESSION STATE BOOTSTRAP ────────────────────────────────────
if 'user'          not in st.session_state: st.session_state.user          = None
if 'impersonating' not in st.session_state: st.session_state.impersonating = None
if 'page'          not in st.session_state: st.session_state.page          = 'dashboard'


# ── MAIN APP ───────────────────────────────────────────────────
def show_app() -> None:
    real = st.session_state.user
    user = st.session_state.impersonating or real
    role = real.get('role')

    inject_sidebar_toggle()

    # Fixed logout button (top-right, always visible)
    if st.button("🚪 Logout", key="global_logout"):
        st.session_state.user          = None
        st.session_state.impersonating = None
        st.session_state.page          = 'dashboard'
        st.rerun()

    # Sidebar: nav + filters
    from portal_pages.sidebar import show_sidebar
    show_sidebar(real, user)

    # Page routing
    page = st.session_state.page
    if page == 'dashboard':
        from portal_pages.dashboard import show_dashboard
        show_dashboard(user)
    elif page == 'reports':
        from portal_pages.reports import show_reports
        show_reports(user)
    elif page == 'cash_flow':
        from portal_pages.cash_flow import show_cash_flow
        show_cash_flow(user)
    elif page == 'downloads':
        from portal_pages.downloads import show_downloads
        show_downloads(user)
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


# ── ROUTER ─────────────────────────────────────────────────────
if st.session_state.user is None:
    from portal_pages.login import show_login
    show_login()
else:
    show_app()
