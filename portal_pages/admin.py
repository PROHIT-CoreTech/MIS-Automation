"""Admin Panel — Client management, permissions, impersonation"""
import streamlit as st
from core.db   import get_conn, get_company_ids_for_user
from core.auth import (create_client, get_all_clients, toggle_client_active,
                        reset_client_password, update_client_permissions,
                        update_client_companies, get_user_by_id)

def show_admin(admin_user):
    st.title("⚙️ Admin Panel")

    tab1, tab2, tab3 = st.tabs(["👥 Client Management", "➕ Create Client", "🔑 Permissions"])

    # ── TAB 1: ALL CLIENTS ────────────────────────────────
    with tab1:
        st.subheader("All Clients")
        clients = get_all_clients()
        if not clients:
            st.info("No clients yet. Create one in 'Create Client' tab.")
        else:
            for c in clients:
                with st.expander(f"{'🟢' if c['is_active'] else '🔴'} {c['full_name'] or c['username']} — {c['companies'] or 'No company assigned'}"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.caption(f"Username: `{c['username']}`")
                        st.caption(f"Excel: {'✅' if c['can_download_excel'] else '❌'} | PPT: {'✅' if c['can_download_ppt'] else '❌'}")
                    with col2:
                        if st.button("👁 View as Client", key=f"imp_{c['id']}"):
                            full = get_user_by_id(c['id'])
                            if full:
                                full_dict = dict(full)
                                full_dict['company_ids'] = get_company_ids_for_user(c['id'], 'client')
                                st.session_state.impersonating = full_dict
                                st.rerun()
                    with col3:
                        label = "🔴 Deactivate" if c['is_active'] else "🟢 Activate"
                        if st.button(label, key=f"tog_{c['id']}"):
                            toggle_client_active(c['id'], not c['is_active'])
                            st.rerun()
                    with col4:
                        new_pass = st.text_input("New Password", key=f"np_{c['id']}", type="password")
                        if st.button("Reset Password", key=f"rp_{c['id']}"):
                            if new_pass:
                                reset_client_password(c['id'], new_pass)
                                st.success("Password reset!")

    # ── TAB 2: CREATE CLIENT ──────────────────────────────
    with tab2:
        st.subheader("Create New Client")
        conn = get_conn()
        companies = conn.execute(
            "SELECT id, display_name FROM companies WHERE is_active=1 ORDER BY display_name"
        ).fetchall()
        conn.close()

        with st.form("create_client_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name *")
                username  = st.text_input("Username *")
                password  = st.text_input("Password *", type="password")
            with col2:
                company_options = {c['display_name']: c['id'] for c in companies}
                selected_cos    = st.multiselect("Assign Companies *", list(company_options.keys()))
                can_excel = st.checkbox("Excel Download", value=True)
                can_ppt   = st.checkbox("PPT Download",   value=False)

            submitted = st.form_submit_button("Create Client", type="primary")
            if submitted:
                if not full_name or not username or not password or not selected_cos:
                    st.error("All fields required")
                else:
                    cids = [company_options[co] for co in selected_cos]
                    try:
                        create_client(username, password, full_name, cids,
                                      can_excel, can_ppt, admin_user['id'])
                        st.success(f"✅ Client '{username}' created successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── TAB 3: PERMISSIONS ────────────────────────────────
    with tab3:
        st.subheader("Update Client Permissions")
        clients = get_all_clients()
        if not clients:
            st.info("No clients yet.")
        else:
            names    = [f"{c['full_name'] or c['username']}" for c in clients]
            selected = st.selectbox("Select Client", names)
            client   = clients[names.index(selected)]

            col1, col2 = st.columns(2)
            with col1:
                new_excel = st.checkbox("Excel Download", value=bool(client['can_download_excel']))
                new_ppt   = st.checkbox("PPT Download",   value=bool(client['can_download_ppt']))
            with col2:
                if st.button("Update Permissions", type="primary"):
                    update_client_permissions(client['id'], new_excel, new_ppt)
                    st.success("Permissions updated!")
