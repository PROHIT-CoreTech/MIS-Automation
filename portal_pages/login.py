"""
portal_pages/login.py — Login page UI.

Extracted from app.py to keep the entry point slim.
"""
import streamlit as st
from core.auth import login, create_session
from core.theme import inject_tilt_js


def show_login(tenant_dict: dict | None = None, super_admin_only: bool = False) -> None:
    """Render the full-screen login page with glassmorphism card, with tenant branding."""
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
            font-size: clamp(30px, 5vw, 42px);
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1.1;
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
 
    # Resolve title and subtitles
    if super_admin_only:
        badge_text = "SYSTEM CONFIGURATION ACCESS"
        title_text = "SaaS <span class=\"grad\">Super Admin</span>"
        sub_text = "Enter platform administrative credentials"
    elif tenant_dict:
        badge_text = f"{tenant_dict['name'].upper()} PORTAL"
        title_text = f"Welcome <span class=\"grad\">back</span>"
        sub_text = f"Sign in to your {tenant_dict['name']} business portal"
    else:
        badge_text = "MIS PORTAL &middot; SECURE ACCESS"
        title_text = "Welcome <span class=\"grad\">back</span>"
        sub_text = "Sign in to your financial intelligence dashboard"

    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.markdown(f"""
            <div style='text-align:center; position:relative; z-index:1;'>
                <div class="badge-pill"><span class="dot"></span>{badge_text}</div>
                <h1 class="login-title">{title_text}</h1>
                <p class="login-sub">{sub_text}</p>
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
 
        # Show back to landing only if not inside a tenant subdomain
        if not tenant_dict:
            if st.button("⬅ Back to Home", use_container_width=True, key="back_to_landing"):
                st.session_state.view = 'landing'
                st.rerun()
 
        st.markdown('<p class="login-footer">Secured &middot; Role-based access &middot; Encrypted</p>',
                    unsafe_allow_html=True)
 
        if submit:
            if not username or not password:
                st.error("Please enter username and password")
            else:
                try:
                    user = login(username.strip(), password)
                    if user:
                        # Enforce Super Admin only on base domain
                        if super_admin_only and user.get('role') != 'super_admin':
                            st.error("❌ Access denied: Super Admin credentials only.")
                        # Enforce tenant isolation on subdomains
                        elif tenant_dict and user.get('tenant_id') != tenant_dict['id']:
                            st.error("❌ Access denied: Invalid credentials for this workspace.")
                        else:
                            st.session_state.user = user
                            st.session_state.page = 'saas_admin' if user.get('role') == 'super_admin' else 'dashboard'
                            
                            # CREATE PERSISTENT SESSION
                            token = create_session(user['id'], hours=24)
                            st.query_params["session"] = token
                            
                            st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                except PermissionError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Login error: {e}")
 
    inject_tilt_js()
