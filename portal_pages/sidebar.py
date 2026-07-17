"""
portal_pages/sidebar.py — Sidebar navigation and global filter widget.

Extracted from app.py (~170 lines of sidebar logic) to keep the
entry point slim. Called by show_app() in app.py.
"""
from __future__ import annotations
from datetime import date as _date

import streamlit as st

from core.auth  import is_admin
from core.db    import get_conn, get_available_months
from core.theme import brand_mark
from core.utils import build_mo_opts, build_yr_mo_map, get_fiscal_year, get_last_fiscal_year

# Quick-select options
_QUICK_OPTIONS = [
    "", "Last 3 Months", "Last 6 Months",
    "Last 12 Months", "Current FY", "Last FY",
]


def _apply_quick_select(quick: str, mo_opts: list, ck: str) -> None:
    """Update session_state from/to keys based on a quick-select choice."""
    today = _date.today()
    n = len(mo_opts)

    if quick == "Last 3 Months":
        st.session_state[f"{ck}_from"] = mo_opts[max(0, n - 3)]
    elif quick == "Last 6 Months":
        st.session_state[f"{ck}_from"] = mo_opts[max(0, n - 6)]
    elif quick == "Last 12 Months":
        st.session_state[f"{ck}_from"] = mo_opts[max(0, n - 12)]
    elif quick == "Current FY":
        fy_start, _ = get_fiscal_year(today)
        sf = f"Apr-{str(fy_start.year)[2:]}"
        st.session_state[f"{ck}_from"] = sf if sf in mo_opts else mo_opts[0]
    elif quick == "Last FY":
        fy_start, fy_end = get_last_fiscal_year(today)
        sf = f"Apr-{str(fy_start.year)[2:]}"
        se = f"Mar-{str(fy_end.year)[2:]}"
        st.session_state[f"{ck}_from"] = sf if sf in mo_opts else mo_opts[0]
        st.session_state[f"{ck}_to"]   = se if se in mo_opts else mo_opts[-1]

    if quick not in ("Last FY", ""):
        st.session_state[f"{ck}_to"] = mo_opts[-1]


def _render_company_selector(user: dict, conn) -> int | None:
    """Render company selector and return selected company_id."""
    st.markdown("""
        <p style='font-size:0.72rem;font-weight:700;letter-spacing:0.10em;
           text-transform:uppercase;color:#6366f1;margin:0 0 6px 0;'>
           🏢 Company
        </p>""", unsafe_allow_html=True)

    if is_admin(user):
        all_cos = conn.execute(
            "SELECT id, display_name FROM companies "
            "WHERE is_active=1 ORDER BY display_name"
        ).fetchall()
        if not all_cos:
            st.session_state['global_company_id']   = None
            st.session_state['global_company_name'] = ''
            st.caption("No companies synced.")
            return None

        co_map  = {c['display_name']: c['id'] for c in all_cos}
        prev    = st.session_state.get('global_company_name', '')
        def_idx = list(co_map.keys()).index(prev) if prev in co_map else 0
        sel = st.selectbox(
            "Company", list(co_map.keys()),
            index=def_idx,
            label_visibility="collapsed",
            key="sb_company",
        )
        st.session_state['global_company_id']   = co_map[sel]
        st.session_state['global_company_name'] = sel
        return co_map[sel]

    else:
        ids = user.get('company_ids', [])
        cid = ids[0] if ids else None
        if cid:
            row   = conn.execute(
                "SELECT display_name FROM companies WHERE id=?", (cid,)
            ).fetchone()
            cname = row['display_name'] if row else ''
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
        return cid


def _render_date_filter(company_id: int) -> None:
    """Render the date-range filter for a selected company."""
    avail = get_available_months(company_id)
    if not avail:
        st.caption("No data synced yet.")
        return

    # Convert to label lists
    mo_opts   = build_mo_opts(
        [{'year': y, 'month': m} for y, m in avail]
    )
    yr_mo_map = build_yr_mo_map(
        [{'year': y, 'month': m} for y, m in avail]
    )

    st.session_state['global_mo_opts']   = mo_opts
    st.session_state['global_yr_mo_map'] = yr_mo_map

    ck = f"gf_{company_id}"

    # Initialise defaults once per company
    if (f"{ck}_from" not in st.session_state or
            st.session_state.get(f"{ck}_from") not in mo_opts):
        st.session_state[f"{ck}_from"]  = (
            mo_opts[-12] if len(mo_opts) >= 12 else mo_opts[0]
        )
        st.session_state[f"{ck}_to"]    = mo_opts[-1]
        st.session_state[f"{ck}_quick"] = ""

    st.markdown("""
        <p style='font-size:0.72rem;font-weight:700;letter-spacing:0.10em;
           text-transform:uppercase;color:#6366f1;margin:10px 0 6px 0;'>
           📅 Date Range
        </p>""", unsafe_allow_html=True)

    # Quick-select dropdown
    quick = st.selectbox(
        "Quick Select", _QUICK_OPTIONS,
        index=_QUICK_OPTIONS.index(st.session_state[f"{ck}_quick"]),
        key=f"{ck}_qs",
    )
    if quick != st.session_state[f"{ck}_quick"]:
        st.session_state[f"{ck}_quick"] = quick
        _apply_quick_select(quick, mo_opts, ck)
        st.rerun()

    # Clamp bounds to available options
    for k in ('_from', '_to'):
        if st.session_state[f"{ck}{k}"] not in mo_opts:
            st.session_state[f"{ck}{k}"] = (
                mo_opts[0] if k == '_from' else mo_opts[-1]
            )

    from_lbl = st.selectbox(
        "From", mo_opts,
        index=mo_opts.index(st.session_state[f"{ck}_from"]),
        key=f"{ck}_fs",
    )
    to_lbl = st.selectbox(
        "To", mo_opts,
        index=mo_opts.index(st.session_state[f"{ck}_to"]),
        key=f"{ck}_ts",
    )

    if st.button("🔄 Reset", use_container_width=True, key="gf_reset"):
        for k in [f"{ck}_from", f"{ck}_to", f"{ck}_quick",
                  f"{ck}_qs",   f"{ck}_fs",  f"{ck}_ts"]:
            st.session_state.pop(k, None)
        st.session_state[f"{ck}_from"]  = (
            mo_opts[-12] if len(mo_opts) >= 12 else mo_opts[0]
        )
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

    # Publish resolved values to shared session keys
    st.session_state['global_from_lbl'] = from_lbl
    st.session_state['global_to_lbl']   = to_lbl
    ym  = yr_mo_map[from_lbl]
    ym2 = yr_mo_map[to_lbl]
    st.session_state['global_from_yr']  = ym[0]
    st.session_state['global_from_mo']  = ym[1]
    st.session_state['global_to_yr']    = ym2[0]
    st.session_state['global_to_mo']    = ym2[1]


def show_sidebar(real: dict, user: dict) -> None:
    """
    Render the full sidebar: brand, user info, navigation, impersonation
    banner, and the shared company + date-range filter.

    Args:
        real: The authenticated (real) user dict.
        user: The currently active user dict (may be an impersonated client).
    """
    role = real.get('role')

    with st.sidebar:
        # 1. Brand header + small in-app Refresh button
        #
        # This is DIFFERENT from a browser refresh (F5) — a browser
        # refresh creates a brand-new Streamlit session, which is why
        # that logs the user out. This button stays inside the SAME
        # session (just triggers a rerun + forced re-sync), so login
        # state is never touched — only the data gets refreshed.
        col_brand, col_refresh = st.columns([5, 1])
        with col_brand:
            st.markdown(
                f'<p class="mis-header">{brand_mark(22)} MIS Portal</p>',
                unsafe_allow_html=True,
            )
        with col_refresh:
            if st.button("🔄", key="sb_refresh", help="Refresh"):
                cid = st.session_state.get('global_company_id')
                if cid:
                    try:
                        from sync.sync_engine import sync_company_now
                        sync_company_now(cid)
                    except Exception:
                        pass  # Tally unreachable — just rerun with existing data
                st.rerun()

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
            ("💵 Cash Flow",   "cash_flow"),
            ("📥 Downloads",   "downloads"),
        ]
        if role == 'admin':
            nav_items += [
                ("⚙️ Admin Panel", "admin"),
                ("🔄 Sync Status", "sync"),
            ]

        for label, key in nav_items:
            is_active = st.session_state.page == key
            if st.button(
                label, key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.page = key
                st.rerun()

        # 4. Impersonation banner
        if st.session_state.impersonating:
            st.warning(f"👁 Viewing as:\n**{user.get('username')}**")
            if st.button("↩️ Exit View", use_container_width=True):
                st.session_state.impersonating = None
                st.session_state.page = 'dashboard'
                st.rerun()

        # 5. Shared filter — Company + Date Range (data pages only)
        if st.session_state.page in ('dashboard', 'reports', 'cash_flow', 'downloads'):
            st.markdown("---")
            conn       = get_conn()
            company_id = _render_company_selector(user, conn)
            conn.close()

            if company_id:
                _render_date_filter(company_id)
