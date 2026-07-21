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
from core.theme import inject_theme

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
if 'view'          not in st.session_state: st.session_state.view          = 'landing'


# ── MAIN APP ───────────────────────────────────────────────────
def show_app() -> None:
    real = st.session_state.user
    user = st.session_state.impersonating or real
    role = real.get('role')

    # Fixed logout button (top-right, always visible)
    if st.button("🚪 Logout", key="global_logout"):
        st.session_state.user          = None
        st.session_state.impersonating = None
        st.session_state.page          = 'dashboard'
        st.session_state.view          = 'landing'
        st.rerun()

    # Sidebar: nav + filters
    from portal_pages.sidebar import show_sidebar
    show_sidebar(real, user)

    # Page routing
    page = st.session_state.page

    # Super Admin Routing
    if role == 'super_admin':
        if page == 'saas_admin':
            from portal_pages.saas_admin import show_saas_admin
            show_saas_admin()
        else:
            st.session_state.page = 'saas_admin'
            st.rerun()
        return

    # Tenant Feature Gating
    import json
    tenant = real.get('tenant')
    if tenant and tenant.get('features'):
        try:
            enabled_features = json.loads(tenant['features'])
        except Exception:
            enabled_features = []
    else:
        # Default features for tenants created without custom features (or default fallback)
        enabled_features = ['dashboard', 'reports', 'cash_flow', 'downloads', 'sync']

    # Gate views based on enabled features & roles
    if page in ('dashboard', 'reports', 'cash_flow', 'downloads'):
        if page not in enabled_features:
            st.error("⛔ This feature is not enabled for your plan.")
            return
    elif page == 'admin':
        if role != 'admin':
            st.error("⛔ Access denied")
            return
    elif page == 'sync':
        if role != 'admin' or 'sync' not in enabled_features:
            st.error("⛔ Access denied")
            return

    # Render pages
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
        from portal_pages.admin import show_admin
        show_admin(real)
    elif page == 'sync':
        from portal_pages.sync_status import show_sync
        show_sync(real)


# ── ROUTER ─────────────────────────────────────────────────────
from core.subdomain import get_current_subdomain, get_tenant_by_subdomain

subdomain = get_current_subdomain()

if subdomain:
    tenant = get_tenant_by_subdomain(subdomain)
    if not tenant:
        st.markdown(f"""
            <div style='text-align:center; padding:100px 20px;'>
                <h1 style='font-size:3.5rem; color:#f43f5e; font-weight:800; margin-bottom:10px;'>404</h1>
                <h2 style='color:#f1f5f9; font-weight:700;'>Workspace Not Found</h2>
                <p style='color:#94a3b8; max-width:500px; margin:20px auto; line-height:1.6;'>
                    The workspace <b>{subdomain}</b> does not exist or has been removed. 
                    Please check the URL or contact your administrator.
                </p>
                <a href='http://localhost:8501/' target='_self' style='color:#6366f1; text-decoration:none; font-weight:600;'>
                    ← Back to MIS Portal
                </a>
            </div>
        """, unsafe_allow_html=True)
    elif not tenant['is_active']:
        st.markdown(f"""
            <div style='text-align:center; padding:100px 20px;'>
                <h1 style='font-size:3.5rem; color:#fbbf24; margin-bottom:10px;'>⚠️</h1>
                <h2 style='color:#f1f5f9; font-weight:700;'>Workspace Suspended</h2>
                <p style='color:#94a3b8; max-width:500px; margin:20px auto; line-height:1.6;'>
                    The workspace <b>{tenant['name']}</b> has been suspended. 
                    Please contact support or your platform administrator.
                </p>
                <a href='http://localhost:8501/' target='_self' style='color:#6366f1; text-decoration:none; font-weight:600;'>
                    ← Back to MIS Portal
                </a>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Valid active tenant subdomain
        if st.session_state.user:
            user_tenant_id = st.session_state.user.get('tenant_id')
            if user_tenant_id != tenant['id']:
                # Mismatch (e.g. Super Admin or client from another tenant) -> force logout
                st.session_state.user = None
                st.session_state.impersonating = None
                st.session_state.page = 'dashboard'
                st.rerun()
            else:
                show_app()
        else:
            # Render login portal customized for this tenant
            from portal_pages.login import show_login
            show_login(tenant)
else:
    # Base Domain (localhost:8501 or misportal.com)
    if st.session_state.user is None:
        if st.session_state.view == 'landing':
            from portal_pages.landing import show_landing
            show_landing()
        else:
            from portal_pages.login import show_login
            show_login(super_admin_only=True)
    else:
        # Logged-in session on base domain
        if st.session_state.user.get('role') == 'super_admin':
            show_app()
        else:
            # Regular user accessed base domain, redirect them to their subdomain link!
            user_tenant = st.session_state.user.get('tenant')
            if user_tenant:
                slug = user_tenant['slug']
                st.markdown(f"""
                    <div style='text-align:center; padding:100px 20px;'>
                        <h2 style='color:#f1f5f9; font-weight:700;'>Redirecting to Your Workspace Portal</h2>
                        <p style='color:#94a3b8; margin:20px 0;'>
                            Please use your organization's custom subdomain link to access the dashboard:
                        </p>
                        <a href='http://{slug}.localhost:8501/' target='_self' style='
                            display:inline-block; background:#6366f1; color:white; 
                            padding:12px 24px; border-radius:12px; text-decoration:none; font-weight:600;
                            box-shadow: 0 4px 20px rgba(99,102,241,0.3); margin-bottom: 24px;'>
                            Go to {user_tenant['name']} Portal
                        </a>
                        <br/>
                    </div>
                """, unsafe_allow_html=True)
                
                # Render manual logout button
                if st.button("🚪 Log Out", key="base_redirect_logout"):
                    st.session_state.user = None
                    st.session_state.impersonating = None
                    st.session_state.page = 'dashboard'
                    st.session_state.view = 'landing'
                    st.rerun()
            else:
                st.session_state.user = None
                st.rerun()
