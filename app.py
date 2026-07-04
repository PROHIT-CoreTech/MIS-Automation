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
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] { display: none; }
        .block-container { padding-top: 0 !important; max-width: 100% !important; }

        .login-orb-1 {
            position: fixed; top: -140px; left: -140px;
            width: 420px; height: 420px; border-radius: 50%;
            background: radial-gradient(circle, rgba(99,102,241,0.20) 0%, transparent 70%);
            pointer-events: none; z-index: 0;
            animation: orbFloat1 9s ease-in-out infinite;
        }
        .login-orb-2 {
            position: fixed; bottom: -100px; right: -100px;
            width: 380px; height: 380px; border-radius: 50%;
            background: radial-gradient(circle, rgba(249,115,22,0.16) 0%, transparent 70%);
            pointer-events: none; z-index: 0;
            animation: orbFloat2 11s ease-in-out infinite;
        }
        .login-orb-3 {
            position: fixed; top: 40%; left: 60%;
            width: 220px; height: 220px; border-radius: 50%;
            background: radial-gradient(circle, rgba(16,185,129,0.10) 0%, transparent 70%);
            pointer-events: none; z-index: 0;
            animation: orbFloat1 7s ease-in-out infinite reverse;
        }
        @keyframes orbFloat1 {
            0%, 100% { transform: translate(0,0) scale(1); }
            50%       { transform: translate(40px, 30px) scale(1.1); }
        }
        @keyframes orbFloat2 {
            0%, 100% { transform: translate(0,0) scale(1); }
            50%       { transform: translate(-30px,-25px) scale(1.08); }
        }
        .login-title {
            font-size: clamp(30px, 5vw, 46px);
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1.06;
            color: #f1f5f9;
            margin: 20px 0 8px 0;
        }
        .login-title .grad {
            background: linear-gradient(135deg, #6366f1, #f97316, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .login-sub {
            color: #64748b;
            font-size: 0.91rem;
            margin: 0 0 28px 0;
        }

        div[data-testid="stForm"] {
            background: linear-gradient(145deg,
                rgba(255,255,255,0.06) 0%,
                rgba(255,255,255,0.02) 100%) !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            border-radius: 28px !important;
            padding: 2.2rem 2.2rem 1.6rem 2.2rem !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            box-shadow:
                0 1px 0 rgba(255,255,255,0.08) inset,
                0 32px 80px rgba(0,0,0,0.55),
                0 0 0 1px rgba(99,102,241,0.15) !important;
            position: relative; z-index: 1;
        }
        .stTextInput input {
            background: rgba(8,12,22,0.6) !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            border-radius: 12px !important;
            color: #f1f5f9 !important;
        }
        .stTextInput input:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
        }
        .login-footer {
            text-align: center; color: #334155;
            font-size: 0.70rem; margin-top: 18px;
            letter-spacing: 0.06em; text-transform: uppercase;
        }
        </style>
        <div class="login-orb-1"></div>
        <div class="login-orb-2"></div>
        <div class="login-orb-3"></div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:5vh'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.markdown("""
            <div style='text-align:center; position:relative; z-index:1;'>
                <div class="badge-pill"><span class="dot"></span>MIS PORTAL &middot; SECURE ACCESS</div>
                <h1 class="login-title">Welcome <span class="grad">back</span></h1>
                <p class="login-sub">Sign in to your financial intelligence dashboard</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="tilt-card">', unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password",
                                     placeholder="Enter your password")
            submit   = st.form_submit_button("Sign In",
                                             use_container_width=True,
                                             type="primary")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<p class="login-footer">Secured &middot; Role-based access &middot; Encrypted</p>',
                    unsafe_allow_html=True)

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
            ("📥 Downloads",   "downloads"),
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

        # ── SHARED FILTER — Company + Date Range ───────────
        # Only shown on data pages; skipped for Admin / Sync pages
        page_now = st.session_state.page
        if page_now in ('dashboard', 'reports', 'downloads'):
            st.markdown("---")
            from core.db import get_conn as _gc
            from datetime import date as _date
            MONTHS_ = ['Jan','Feb','Mar','Apr','May','Jun',
                       'Jul','Aug','Sep','Oct','Nov','Dec']
            _conn = _gc()

            # ── Company selector ──────────────────────────
            st.markdown("""
                <p style='font-size:0.72rem;font-weight:700;letter-spacing:0.10em;
                   text-transform:uppercase;color:#6366f1;margin:0 0 6px 0;'>
                   🏢 Company
                </p>""", unsafe_allow_html=True)

            if is_admin(user):
                all_cos = _conn.execute(
                    "SELECT id, display_name FROM companies "
                    "WHERE is_active=1 ORDER BY display_name"
                ).fetchall()
                if all_cos:
                    co_map = {c['display_name']: c['id'] for c in all_cos}
                    # Persist last selected company
                    prev = st.session_state.get('global_company_name','')
                    def_idx = list(co_map.keys()).index(prev) \
                              if prev in co_map else 0
                    sel = st.selectbox(
                        "Company", list(co_map.keys()),
                        index=def_idx,
                        label_visibility="collapsed",
                        key="sb_company"
                    )
                    st.session_state['global_company_id']   = co_map[sel]
                    st.session_state['global_company_name'] = sel
                else:
                    st.session_state['global_company_id']   = None
                    st.session_state['global_company_name'] = ''
                    st.caption("No companies synced.")
            else:
                ids = user.get('company_ids', [])
                cid = ids[0] if ids else None
                if cid:
                    co = _conn.execute(
                        "SELECT display_name FROM companies WHERE id=?", (cid,)
                    ).fetchone()
                    cname = co['display_name'] if co else ''
                else:
                    cname = ''
                st.session_state['global_company_id']   = cid
                st.session_state['global_company_name'] = cname
                st.markdown(f"""
                    <div style='background:rgba(99,102,241,0.08);border:1px solid
                        rgba(99,102,241,0.2);border-radius:10px;padding:8px 12px;
                        font-weight:600;font-size:0.85rem;'>
                        {cname}
                    </div>""", unsafe_allow_html=True)

            company_id = st.session_state.get('global_company_id')

            # ── Date range (only when a company is selected) ──
            if company_id:
                avail = _conn.execute(
                    "SELECT DISTINCT year, month FROM pl_data "
                    "WHERE company_id=? ORDER BY year, month", (company_id,)
                ).fetchall()
                _conn.close()

                if avail:
                    mo_opts = [
                        f"{MONTHS_[int(r['month'])-1]}-{str(int(r['year']))[2:]}"
                        for r in avail
                    ]
                    yr_mo_map = {
                        f"{MONTHS_[int(r['month'])-1]}-{str(int(r['year']))[2:]}":
                        (int(r['year']), int(r['month'])) for r in avail
                    }
                    # Store available options for pages
                    st.session_state['global_mo_opts']   = mo_opts
                    st.session_state['global_yr_mo_map'] = yr_mo_map

                    today_ = _date.today()
                    # Init defaults if not set or company changed
                    ck = f"gf_{company_id}"
                    if (f"{ck}_from" not in st.session_state or
                            st.session_state.get(f"{ck}_from") not in mo_opts):
                        st.session_state[f"{ck}_from"]  = (
                            mo_opts[-12] if len(mo_opts) >= 12 else mo_opts[0])
                        st.session_state[f"{ck}_to"]    = mo_opts[-1]
                        st.session_state[f"{ck}_quick"] = ""

                    st.markdown("""
                        <p style='font-size:0.72rem;font-weight:700;letter-spacing:0.10em;
                           text-transform:uppercase;color:#6366f1;margin:10px 0 6px 0;'>
                           📅 Date Range
                        </p>""", unsafe_allow_html=True)

                    # Quick select
                    QS = ["", "Last 3 Months", "Last 6 Months",
                          "Last 12 Months", "Current FY", "Last FY"]
                    quick = st.selectbox(
                        "Quick Select", QS,
                        index=QS.index(st.session_state[f"{ck}_quick"]),
                        key=f"{ck}_qs"
                    )
                    if quick != st.session_state[f"{ck}_quick"]:
                        st.session_state[f"{ck}_quick"] = quick
                        n = len(mo_opts)
                        if   quick == "Last 3 Months":  st.session_state[f"{ck}_from"] = mo_opts[max(0,n-3)]
                        elif quick == "Last 6 Months":  st.session_state[f"{ck}_from"] = mo_opts[max(0,n-6)]
                        elif quick == "Last 12 Months": st.session_state[f"{ck}_from"] = mo_opts[max(0,n-12)]
                        elif quick == "Current FY":
                            fy = today_.year if today_.month >= 4 else today_.year - 1
                            sf = f"Apr-{str(fy)[2:]}"
                            st.session_state[f"{ck}_from"] = sf if sf in mo_opts else mo_opts[0]
                        elif quick == "Last FY":
                            fy = (today_.year-1) if today_.month >= 4 else (today_.year-2)
                            sf = f"Apr-{str(fy)[2:]}"; se = f"Mar-{str(fy+1)[2:]}"
                            st.session_state[f"{ck}_from"] = sf if sf in mo_opts else mo_opts[0]
                            st.session_state[f"{ck}_to"]   = se if se in mo_opts else mo_opts[-1]
                        if quick not in ("Last FY", ""):
                            st.session_state[f"{ck}_to"] = mo_opts[-1]
                        st.rerun()

                    # Validate bounds
                    for k in ('_from', '_to'):
                        if st.session_state[f"{ck}{k}"] not in mo_opts:
                            st.session_state[f"{ck}{k}"] = (
                                mo_opts[0] if k == '_from' else mo_opts[-1])

                    from_lbl = st.selectbox(
                        "From", mo_opts,
                        index=mo_opts.index(st.session_state[f"{ck}_from"]),
                        key=f"{ck}_fs"
                    )
                    to_lbl = st.selectbox(
                        "To", mo_opts,
                        index=mo_opts.index(st.session_state[f"{ck}_to"]),
                        key=f"{ck}_ts"
                    )

                    if st.button("🔄 Reset", use_container_width=True, key="gf_reset"):
                        for k in [f"{ck}_from", f"{ck}_to", f"{ck}_quick",
                                  f"{ck}_qs",   f"{ck}_fs",  f"{ck}_ts"]:
                            st.session_state.pop(k, None)
                        st.session_state[f"{ck}_from"]  = (
                            mo_opts[-12] if len(mo_opts) >= 12 else mo_opts[0])
                        st.session_state[f"{ck}_to"]    = mo_opts[-1]
                        st.session_state[f"{ck}_quick"] = ""
                        st.rerun()

                    if from_lbl != st.session_state[f"{ck}_from"]:
                        st.session_state[f"{ck}_from"]  = from_lbl
                        st.session_state[f"{ck}_quick"] = ""
                        st.rerun()
                    if to_lbl != st.session_state[f"{ck}_to"]:
                        st.session_state[f"{ck}_to"]    = to_lbl
                        st.session_state[f"{ck}_quick"] = ""
                        st.rerun()

                    # Write resolved values to shared keys
                    st.session_state['global_from_lbl'] = from_lbl
                    st.session_state['global_to_lbl']   = to_lbl
                    ym = yr_mo_map[from_lbl]
                    st.session_state['global_from_yr']  = ym[0]
                    st.session_state['global_from_mo']  = ym[1]
                    ym2 = yr_mo_map[to_lbl]
                    st.session_state['global_to_yr']    = ym2[0]
                    st.session_state['global_to_mo']    = ym2[1]
                else:
                    _conn.close()
                    st.caption("No data synced yet.")
            else:
                _conn.close()

    # ── PAGE ROUTING ───────────────────────────────────────
    page = st.session_state.page
    if page == 'dashboard':
        from portal_pages.dashboard import show_dashboard
        show_dashboard(user)
    elif page == 'reports':
        from portal_pages.reports import show_reports
        show_reports(user)
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


# ── ROUTER ─────────────────────────────────────────────────
if st.session_state.user is None:
    show_login()
else:
    show_app()
