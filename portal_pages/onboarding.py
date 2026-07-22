import streamlit as st
import time
import re
from core.db import get_conn
from core.auth import create_tenant, create_tenant_admin
from core.theme import inject_theme

def show_onboarding():
    inject_theme()
    
    # Hide sidebar
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] { display: none; }
        .block-container { 
            padding-top: 2rem !important; 
            max-width: 800px !important; 
            margin: 0 auto !important;
        }

        .step-header {
            font-size: 1.5rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 8px;
        }
        .step-caption {
            color: #94a3b8;
            margin-bottom: 24px;
        }
        .progress-bar-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            position: relative;
        }
        .progress-bar-line {
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 2px;
            background: rgba(255,255,255,0.1);
            z-index: 0;
        }
        .progress-bar-fill {
            position: absolute;
            top: 50%;
            left: 0;
            height: 2px;
            background: #6366f1;
            z-index: 0;
            transition: width 0.3s ease;
        }
        .progress-step {
            z-index: 1;
            background: #0f1629;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.9rem;
            border: 2px solid rgba(255,255,255,0.1);
            color: #94a3b8;
        }
        .progress-step.active {
            border-color: #6366f1;
            background: #6366f1;
            color: white;
            box-shadow: 0 0 15px rgba(99,102,241,0.5);
        }
        .progress-step.completed {
            border-color: #6366f1;
            color: #6366f1;
        }
        </style>
    """, unsafe_allow_html=True)

    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 1

    step = st.session_state.onboarding_step
    plan_name = st.session_state.get('onboarding_plan', 'Selected Plan')
    plan_price = st.session_state.get('onboarding_price', '')
    plan_features = st.session_state.get('onboarding_features', [])

    # Cancel onboarding button (top right)
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"## Account Registration: {plan_name}")
    with col2:
        st.markdown("<div style='padding-top: 10px;'>", unsafe_allow_html=True)
        if st.button("Cancel", key="cancel_onboarding"):
            st.session_state.view = 'landing'
            st.session_state.pop('onboarding_step', None)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Progress bar
    fill_width = (step - 1) * 33.33
    st.markdown(f"""
        <div class="progress-bar-container">
            <div class="progress-bar-line"></div>
            <div class="progress-bar-fill" style="width: {fill_width}%;"></div>
            <div class="progress-step {'active' if step == 1 else 'completed' if step > 1 else ''}">1</div>
            <div class="progress-step {'active' if step == 2 else 'completed' if step > 2 else ''}">2</div>
            <div class="progress-step {'active' if step == 3 else 'completed' if step > 3 else ''}">3</div>
            <div class="progress-step {'active' if step == 4 else 'completed' if step > 4 else ''}">4</div>
        </div>
        <div style="display:flex; justify-content:space-between; color:#94a3b8; font-size:0.8rem; padding: 0 10px;">
            <span>Payment</span>
            <span>Tenant</span>
            <span>Admin</span>
            <span>Finish</span>
        </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        # ── STEP 1: PAYMENT ─────────────────────────────────────────────
        if step == 1:
            st.markdown('<div class="step-header">💳 Step 1: Payment Details</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="step-caption">Complete your checkout for the <b>{plan_name}</b> ({plan_price}).</div>', unsafe_allow_html=True)
            
            cardholder = st.text_input("Cardholder Name", placeholder="Jane Doe")
            c1, c2, c3 = st.columns([2, 1, 1])
            card_num = c1.text_input("Card Number", placeholder="•••• •••• •••• ••••")
            expiry = c2.text_input("Expiry", placeholder="MM/YY")
            cvv = c3.text_input("CVV", type="password", placeholder="•••")
            
            st.write("")
            if st.button("💸 Pay Now", type="primary"):
                card_clean = card_num.replace(" ", "").replace("-", "")
                
                if not cardholder or not card_num or not expiry or not cvv:
                    st.error("Please fill out all payment details.")
                elif not re.match(r"^\d{13,19}$", card_clean):
                    st.error("Card number must be valid (13-19 digits).")
                elif not re.match(r"^(0[1-9]|1[0-2])/?([0-9]{2})$", expiry):
                    st.error("Expiry must be in MM/YY format.")
                elif not re.match(r"^\d{3,4}$", cvv):
                    st.error("CVV must be 3 or 4 digits.")
                else:
                    with st.spinner("Processing secure payment..."):
                        time.sleep(1.5)
                    st.session_state.onboarding_step = 2
                    st.rerun()

        # ── STEP 2: ADD TENANT ──────────────────────────────────────────
        elif step == 2:
            st.markdown('<div class="step-header">🏢 Step 2: Add Tenant</div>', unsafe_allow_html=True)
            st.markdown('<div class="step-caption">Set up your workspace name and custom subdomain slug.</div>', unsafe_allow_html=True)
            
            workspace_name = st.text_input("Tenant Name", placeholder="Acme Corporation", value=st.session_state.get('reg_name', ''))
            workspace_slug = st.text_input("Portal Subdomain Slug", placeholder="acme (letters/numbers only)", value=st.session_state.get('reg_slug', ''))
            
            st.write("")
            col_back, col_next = st.columns(2)
            with col_back:
                if st.button("⬅ Back"):
                    st.session_state.onboarding_step = 1
                    st.rerun()
            with col_next:
                if st.button("Next ➡", type="primary"):
                    slug_clean = workspace_slug.lower().strip()
                    
                    # Check unique slug in database
                    conn = get_conn()
                    existing = conn.execute("SELECT id FROM tenants WHERE slug=?", (slug_clean,)).fetchone()
                    conn.close()
                    
                    if not workspace_name or not slug_clean:
                        st.error("Workspace name and slug are required.")
                    elif not re.match(r"^[a-z0-9_\-]+$", slug_clean):
                        st.error("Slug must contain only lowercase letters, numbers, hyphens, or underscores.")
                    elif existing:
                        st.error(f"The subdomain slug '{slug_clean}' is already taken. Please choose another.")
                    else:
                        st.session_state.reg_name = workspace_name
                        st.session_state.reg_slug = slug_clean
                        st.session_state.onboarding_step = 3
                        st.rerun()

        # ── STEP 3: CREATE FIRST USER ───────────────────────────────────
        elif step == 3:
            st.markdown('<div class="step-header">👤 Step 3: Create Admin User</div>', unsafe_allow_html=True)
            st.markdown('<div class="step-caption">Set up the administrator account for your new workspace.</div>', unsafe_allow_html=True)
            
            admin_name = st.text_input("Admin Full Name", placeholder="John Doe")
            admin_user = st.text_input("Admin Username", placeholder="john_admin")
            admin_pass = st.text_input("Admin Password", type="password", placeholder="••••••••")
            
            st.write("")
            col_back, col_next = st.columns(2)
            with col_back:
                if st.button("⬅ Back"):
                    st.session_state.onboarding_step = 2
                    st.rerun()
            with col_next:
                if st.button("🚀 Register & Activate Workspace", type="primary"):
                    if not admin_name or not admin_user or not admin_pass:
                        st.error("All admin fields are required.")
                    else:
                        with st.spinner("Provisioning workspace and admin user..."):
                            t_id = create_tenant(st.session_state.reg_name, st.session_state.reg_slug, plan_name, plan_features)
                            create_tenant_admin(t_id, admin_user, admin_pass, admin_name)
                            
                            st.session_state.onboarding_step = 4
                            st.rerun()

        # ── STEP 4: DISPLAY DOMAIN ──────────────────────────────────────
        elif step == 4:
            slug = st.session_state.reg_slug
            name = st.session_state.reg_name
            
            st.balloons()
            st.markdown('<div class="step-header">🎉 Step 4: Setup Complete!</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="step-caption">Workspace <b>{name}</b> has been successfully created.</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
                Your custom tenant login portal is ready at:
                <br/><br/>
                <div style='background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2); 
                     border-radius:12px; padding:20px; font-weight:600; text-align:center; font-size:1.3rem; margin-bottom:24px;'>
                    <a href='http://{slug}.localhost:8501/' target='_self' style='color:#6366f1; text-decoration:none;'>
                        http://{slug}.localhost:8501
                    </a>
                </div>
                Click the link above or the button below to navigate to your branded login screen and start using the portal.
            """, unsafe_allow_html=True)
            
            st.write("")
            col_home, col_go = st.columns(2)
            with col_home:
                if st.button("Return Home"):
                    st.session_state.pop('onboarding_step', None)
                    st.session_state.pop('onboarding_plan', None)
                    st.session_state.pop('onboarding_price', None)
                    st.session_state.pop('onboarding_features', None)
                    st.session_state.pop('reg_name', None)
                    st.session_state.pop('reg_slug', None)
                    st.session_state.view = 'landing'
                    st.rerun()
            with col_go:
                st.markdown(f"""
                    <a href='http://{slug}.localhost:8501/' target='_self' style='
                        display:block; text-align:center; background:#6366f1; color:white; 
                        padding:10px 16px; border-radius:8px; text-decoration:none; font-weight:600;'>
                        🚀 Go to Portal
                    </a>
                """, unsafe_allow_html=True)
