import streamlit as st
import json
from core.auth import get_all_tenants, create_tenant, create_tenant_admin, update_tenant

def show_saas_admin():
    """Render the SaaS Super Admin Portal."""
    st.markdown("## ⚙️ SaaS Admin Portal")
    st.caption("Manage platform tenants, subscription plans, and active feature gates.")
    st.divider()

    tab1, tab2 = st.tabs(["🏢 Manage Tenants", "➕ Create Tenant"])

    # ── TAB 1: MANAGE TENANTS ───────────────────────────
    with tab1:
        st.subheader("All Registered Tenants")
        tenants = get_all_tenants()
        
        if not tenants:
            st.info("No tenants registered yet. Create one in the 'Create Tenant' tab.")
        else:
            for t in tenants:
                # Resolve features
                try:
                    features_list = json.loads(t['features'])
                except Exception:
                    features_list = []
                
                status_label = "🟢 Active" if t['is_active'] else "🔴 Suspended"
                title = f"{t['name']} ({t['slug']}) — {t['plan_name']} | {status_label}"
                
                with st.expander(title):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Tenant Details**")
                        st.write(f"ID: `{t['id']}`")
                        st.write(f"Created At: `{t['created_at']}`")
                        st.write(f"Active Client Accounts: `{t['client_count']}`")
                        
                        # Active status toggle
                        new_status = st.toggle("Tenant Active", value=bool(t['is_active']), key=f"status_toggle_{t['id']}")
                    
                    with col2:
                        st.markdown(f"**Plan & Features**")
                        new_plan = st.selectbox(
                            "Plan Level", ["Bronze", "Silver", "Gold"], 
                            index=["Bronze", "Silver", "Gold"].index(t['plan_name']) if t['plan_name'] in ["Bronze", "Silver", "Gold"] else 1,
                            key=f"plan_select_{t['id']}"
                        )
                        
                        available_features = {
                            "📊 Dashboard": "dashboard",
                            "📄 MIS Reports": "reports",
                            "💵 Cash Flow": "cash_flow",
                            "📥 Downloads": "downloads",
                            "🔄 Tally Sync": "sync"
                        }
                        
                        # Pre-select active features
                        default_selected = [k for k, v in available_features.items() if v in features_list]
                        
                        selected_features_keys = st.multiselect(
                            "Configure Features", 
                            list(available_features.keys()),
                            default=default_selected,
                            key=f"feat_select_{t['id']}"
                        )
                        
                        resolved_features = [available_features[k] for k in selected_features_keys]
                    
                    st.write("")
                    if st.button("💾 Save Changes", key=f"save_tenant_{t['id']}", type="primary"):
                        try:
                            update_tenant(t['id'], new_plan, resolved_features, new_status)
                            st.success(f"Tenant '{t['name']}' updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating tenant: {e}")

    # ── TAB 2: CREATE TENANT ────────────────────────────
    with tab2:
        st.subheader("Register a New Tenant")
        st.caption("This will create a new tenant environment and assign a default Tenant Administrator.")
        
        with st.form("create_tenant_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Company Details**")
                tenant_name = st.text_input("Tenant Organization Name *", placeholder="e.g. Hooli Inc.")
                tenant_slug = st.text_input("Unique URL/Slug *", placeholder="e.g. hooli (letters/numbers only)")
                tenant_plan = st.selectbox("Plan Level *", ["Bronze", "Silver", "Gold"], index=1)
                
                feat_opts = {
                    "📊 Dashboard": "dashboard",
                    "📄 MIS Reports": "reports",
                    "💵 Cash Flow": "cash_flow",
                    "📥 Downloads": "downloads",
                    "🔄 Tally Sync": "sync"
                }
                
                selected_feats_keys = st.multiselect(
                    "Enable Features *", 
                    list(feat_opts.keys()), 
                    default=["📊 Dashboard", "📄 MIS Reports", "📥 Downloads", "🔄 Tally Sync"]
                )
                
            with col2:
                st.markdown("**Tenant Administrator Account**")
                admin_name = st.text_input("Admin Full Name *", placeholder="e.g. Richard Hendricks")
                admin_user = st.text_input("Admin Username *", placeholder="e.g. richard_admin")
                admin_pass = st.text_input("Admin Password *", type="password", placeholder="Enter secure password")
                
            submitted = st.form_submit_button("🚀 Register Tenant & Create Admin", type="primary", use_container_width=True)
            
            if submitted:
                # Validation
                slug_clean = tenant_slug.lower().strip()
                import re
                if not tenant_name or not tenant_slug or not admin_name or not admin_user or not admin_pass:
                    st.error("⚠️ All required fields (*) must be filled.")
                elif not re.match(r"^[a-z0-9_\-]+$", slug_clean):
                    st.error("⚠️ Slug must contain only lowercase letters, numbers, hyphens, or underscores.")
                elif not selected_feats_keys:
                    st.error("⚠️ You must enable at least one feature.")
                else:
                    try:
                        resolved_feats = [feat_opts[k] for k in selected_feats_keys]
                        # 1. Create Tenant
                        new_id = create_tenant(tenant_name, slug_clean, tenant_plan, resolved_feats)
                        # 2. Create Tenant Admin
                        create_tenant_admin(new_id, admin_user, admin_pass, admin_name)
                        
                        st.success(f"🎉 Tenant '{tenant_name}' created successfully with Admin '{admin_user}'!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error creating tenant: {e}")
