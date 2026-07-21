import streamlit as st
import json
import pandas as pd
from core.db import get_conn
from core.auth import get_all_tenants, create_tenant, create_tenant_admin, update_tenant

def show_saas_admin():
    """Render the SaaS Super Admin Portal."""
    st.markdown("## ⚙️ SaaS Admin Portal")
    st.caption("Manage platform tenants, subscription plans, and active feature gates.")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🏢 Manage Tenants", "➕ Create Tenant"])

    # ── TAB 1: DASHBOARD ────────────────────────────────────────
    with tab1:
        st.subheader("Platform Overview")
        tenants = get_all_tenants()
        
        conn = get_conn()
        total_users = conn.execute("SELECT COUNT(id) FROM users").fetchone()[0]
        conn.close()
        
        # Calculate revenue and metrics
        plan_prices = {"Bronze": 2999, "Silver": 4999, "Gold": 9999}
        active_tenants = [t for t in tenants if t['is_active']]
        
        def get_price(plan_name):
            clean_name = str(plan_name).replace(" Plan", "").strip()
            return plan_prices.get(clean_name, 0)
        
        total_mrr = sum(get_price(t['plan_name']) for t in active_tenants)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Monthly Revenue", f"₹{total_mrr:,.0f}")
        col2.metric("Active Subscriptions", len(active_tenants))
        col3.metric("Total Platform Users", total_users)
        
        st.divider()
        st.subheader("Revenue by Plan")
        
        if active_tenants:
            revenue_by_plan = {"Bronze": 0, "Silver": 0, "Gold": 0}
            for t in active_tenants:
                raw_plan = t['plan_name']
                clean_plan = str(raw_plan).replace(" Plan", "").strip()
                if clean_plan in revenue_by_plan:
                    revenue_by_plan[clean_plan] += get_price(raw_plan)
                    
            import plotly.graph_objects as go
            
            # Map plans to modern, premium colors
            plan_colors = {
                "Bronze": "#d97706", # Rich amber/bronze
                "Silver": "#94a3b8", # Elegant slate/silver
                "Gold":   "#eab308"  # Bright gold
            }
            plan_names = list(revenue_by_plan.keys())
            plan_revenues = list(revenue_by_plan.values())
            
            total_revenue = sum(plan_revenues)
            
            # Modern Donut Chart
            fig = go.Figure(data=[
                go.Pie(
                    labels=plan_names,
                    values=plan_revenues,
                    hole=0.75,
                    marker=dict(
                        colors=[plan_colors.get(p, "#6366f1") for p in plan_names],
                        line=dict(color='#0e1117', width=5) # sleek dark gap between slices matching standard Streamlit dark bg
                    ),
                    textinfo='label+percent',
                    textfont=dict(size=14, color='#f1f5f9', family='Inter, sans-serif'),
                    hovertemplate='<b>%{label} Plan</b><br>Revenue: ₹%{value:,.0f}<extra></extra>',
                    direction='clockwise',
                    sort=False
                )
            ])
            
            fig.update_layout(
                margin=dict(l=10, r=10, t=30, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                hoverlabel=dict(
                    bgcolor="#1e293b",
                    bordercolor="#334155",
                    font_size=14,
                    font_family="Inter, sans-serif"
                ),
                annotations=[dict(
                    text=f"<b>Total</b><br><span style='font-size:26px; color:#f8fafc'>₹{total_revenue:,.0f}</span>",
                    x=0.5, y=0.5,
                    font_size=16,
                    font_color="#94a3b8",
                    font_family="Inter, sans-serif",
                    showarrow=False
                )]
            )
            
            # Use config to hide the modebar for a cleaner look
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
        else:
            st.info("No active subscriptions to display revenue.")
            
        st.divider()
        st.subheader("Tenant Payment Details")
        if tenants:
            payment_data = []
            for t in tenants:
                price = get_price(t['plan_name'])
                payment_data.append({
                    "Tenant Name": t['name'],
                    "Subdomain": f"{t['slug']}.localhost:8501",
                    "Plan Level": t['plan_name'],
                    "Monthly Rate (₹)": f"₹{price:,.0f}" if t['is_active'] else "₹0 (Suspended)",
                    "Status": "🟢 Active" if t['is_active'] else "🔴 Suspended"
                })
            st.dataframe(pd.DataFrame(payment_data), width="stretch", hide_index=True)
        else:
            st.info("No tenants registered.")

    # ── TAB 2: MANAGE TENANTS ───────────────────────────
    with tab2:
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
                        st.write(f"Current Plan: `{t['plan_name']}`")
                        st.markdown(f"Subdomain URL: <a href='http://{t['slug']}.localhost:8501/' target='_blank'>http://{t['slug']}.localhost:8501/</a>", unsafe_allow_html=True)
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

    # ── TAB 3: CREATE TENANT ────────────────────────────
    with tab3:
        st.subheader("Register a New Tenant")
        st.caption("This will create a new tenant environment and assign a default Tenant Administrator.")
        
        with st.form("create_tenant_form", clear_on_submit=True):
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
                
                plan_defaults = {
                    "Bronze": ["📊 Dashboard", "📥 Downloads"],
                    "Silver": ["📊 Dashboard", "📄 MIS Reports", "📥 Downloads", "🔄 Tally Sync"],
                    "Gold": ["📊 Dashboard", "📄 MIS Reports", "💵 Cash Flow", "📥 Downloads", "🔄 Tally Sync"]
                }
                
                selected_feats_keys = st.multiselect(
                    "Enable Features *", 
                    list(feat_opts.keys()), 
                    default=plan_defaults.get(tenant_plan, ["📊 Dashboard"])
                )
                
            with col2:
                st.markdown("**Tenant Administrator Account**")
                admin_name = st.text_input("Admin Full Name *", placeholder="e.g. Richard Hendricks")
                admin_user = st.text_input("Admin Username *", placeholder="e.g. richard_admin")
                admin_pass = st.text_input("Admin Password *", type="password", placeholder="Enter secure password")
                
            st.write("")
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
                        # No st.rerun() needed because st.form(clear_on_submit=True) automatically clears fields
                        # and allowing execution to finish displays the success message!
                    except Exception as e:
                        st.error(f"❌ Error creating tenant: {e}")
