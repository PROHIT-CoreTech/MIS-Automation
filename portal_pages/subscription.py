import streamlit as st
import json
from datetime import datetime, timedelta

def show_subscription(user: dict):
    st.markdown("## 💳 Subscription Details")
    st.caption("Manage your workspace plan and billing.")
    st.divider()
    
    tenant = user.get('tenant')
    if not tenant:
        st.error("Tenant information not found.")
        return
        
    try:
        # Expected format: "2026-07-21 05:30:14"
        created_at = datetime.fromisoformat(tenant.get('created_at', datetime.now().isoformat()))
    except Exception:
        created_at = datetime.now()
        
    due_date = created_at + timedelta(days=30) # Monthly billing
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Current Plan**")
        st.info(tenant.get('plan_name', 'Standard'))
    with col2:
        st.markdown("**Status**")
        if tenant.get('is_active'):
            st.success("🟢 Active")
        else:
            st.error("🔴 Suspended")
    with col3:
        st.markdown("**Renewal Date**")
        st.warning(due_date.strftime("%d %B, %Y"))
        
    st.markdown("### 🌟 Enabled Features")
    try:
        features = json.loads(tenant.get('features', '[]'))
    except Exception:
        features = []
        
    if not features:
        st.write("No premium features currently active.")
    else:
        for f in features:
            st.write(f"- ✅ {f.title().replace('_', ' ')}")
