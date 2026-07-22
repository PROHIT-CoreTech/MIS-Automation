import streamlit as st
from core.theme import inject_theme, inject_tilt_js




def show_landing() -> None:
    """Render the premium SaaS landing page."""
    inject_theme()

    # Hide sidebar & set wide padding
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] { display: none; }
        .block-container { 
            padding-top: 0 !important; 
            padding-bottom: 3rem !important;
            max-width: 1200px !important; 
            margin: 0 auto !important;
        }
        
        /* Floating background elements */
        .landing-orb-1 {
            position: fixed; top: -100px; left: -100px;
            width: 500px; height: 500px; border-radius: 50%;
            background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);
            pointer-events: none; z-index: 0;
            animation: orbFloat 12s ease-in-out infinite;
        }
        .landing-orb-2 {
            position: fixed; bottom: -50px; right: -50px;
            width: 450px; height: 450px; border-radius: 50%;
            background: radial-gradient(circle, rgba(249,115,22,0.08) 0%, transparent 70%);
            pointer-events: none; z-index: 0;
            animation: orbFloat 15s ease-in-out infinite reverse;
        }
        
        @keyframes orbFloat {
            0%, 100% { transform: translate(0, 0) scale(1); }
            50% { transform: translate(30px, 40px) scale(1.05); }
        }

        /* Hero styles */
        .hero-section {
            text-align: center;
            padding: 80px 20px 40px 20px;
            position: relative;
            z-index: 1;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(99,102,241,0.1);
            border: 1px solid rgba(99,102,241,0.25);
            padding: 6px 16px;
            border-radius: 99px;
            font-size: 0.75rem;
            font-weight: 700;
            color: #818cf8;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 24px;
        }
        .hero-title {
            font-size: clamp(34px, 5vw, 56px);
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1.05;
            color: #f8fafc;
            margin-bottom: 20px;
        }
        .hero-title span {
            background: linear-gradient(135deg, #6366f1 30%, #f97316 70%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .hero-desc {
            font-size: clamp(16px, 2.5vw, 20px);
            color: #94a3b8;
            max-width: 700px;
            margin: 0 auto 36px auto;
            line-height: 1.5;
        }

        /* Feature section */
        .section-title {
            text-align: center;
            font-size: 2rem;
            font-weight: 800;
            color: #f1f5f9;
            margin: 60px 0 30px 0;
            letter-spacing: -0.03em;
        }
        .landing-card {
            background: rgba(15, 22, 41, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 20px;
            padding: 28px;
            backdrop-filter: blur(12px);
            height: 100%;
            transition: all 0.22s ease;
        }
        .landing-card:hover {
            border-color: rgba(99, 102, 241, 0.3);
            transform: translateY(-4px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
        }
        .card-icon {
            font-size: 2rem;
            margin-bottom: 16px;
        }
        .card-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 10px;
        }
        .card-desc {
            font-size: 0.88rem;
            color: #94a3b8;
            line-height: 1.45;
        }

        /* Pricing Card */
        .pricing-card {
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.005) 100%), rgba(15, 22, 41, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 24px;
            padding: 32px 28px 16px 28px;
            margin-bottom: -16px;
            backdrop-filter: blur(12px);
            text-align: center;
            position: relative;
            overflow: hidden;
            transition: all 0.25s ease;
        }
        .pricing-card.popular {
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.1);
        }
        .pricing-card.popular::before {
            content: 'POPULAR';
            position: absolute; top: 18px; right: -30px;
            background: #6366f1;
            color: white; font-size: 0.65rem; font-weight: 800;
            padding: 4px 30px; transform: rotate(45deg);
            letter-spacing: 0.05em;
        }
        .pricing-card:hover {
            border-color: rgba(99, 102, 241, 0.4);
            transform: translateY(-5px);
            box-shadow: 0 16px 40px rgba(0,0,0,0.5);
        }
        .plan-name {
            font-size: 1.1rem;
            font-weight: 700;
            color: #94a3b8;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 12px;
        }
        .plan-price {
            font-size: 2.5rem;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 24px;
        }
        .plan-price span {
            font-size: 0.9rem;
            color: #64748b;
            font-weight: 500;
        }
        .plan-feature-list {
            text-align: left;
            margin: 24px 0 12px 0;
            list-style: none;
            padding: 0;
        }
        .plan-feature-item {
            font-size: 0.88rem;
            color: #cbd5e1;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .plan-feature-item.disabled {
            color: #475569;
            text-decoration: line-through;
        }
        </style>
        
        <div class="landing-orb-1"></div>
        <div class="landing-orb-2"></div>
    """, unsafe_allow_html=True)

    # 1. Header & Navigation (Super Admin button only)
    col_logo, col_space, col_login = st.columns([4, 5, 2])
    with col_logo:
        st.markdown("""
            <div style='display:flex; align-items:center; gap:8px; padding-top:20px;'>
                <span style='font-size:1.6rem; font-weight:800; color:#f1f5f9;'>📊 MIS Portal</span>
            </div>
        """, unsafe_allow_html=True)
    with col_login:
        st.write("") # Spacer
        st.write("")
        if st.button("🔑 Super Admin Access", key="top_login_btn"):
            st.session_state.view = 'login'
            st.rerun()

    # 2. Hero Section
    st.markdown("""
        <div class="hero-section">
            <div class="hero-badge"><span class="badge-dot"></span>Automated Tally Prime Sync</div>
            <h1 class="hero-title">Automate your financial intelligence <span>instantly</span></h1>
            <p class="hero-desc">Connect Tally Prime directly to a beautiful, interactive, and role-isolated dashboard. Deliver detailed MIS reports, P&L breakups, and ageing lists to clients automatically.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 3. Features Section
    st.markdown('<h2 class="section-title">Everything you need to automate reporting</h2>', unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""
            <div class="landing-card">
                <div class="card-icon">📈</div>
                <div class="card-title">Live KPI Dashboards</div>
                <div class="card-desc">Track Revenue, Gross Profit, and Net Profit trends in real-time. Analyze performance using premium, multi-dimensional Plotly charts.</div>
            </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
            <div class="landing-card">
                <div class="card-icon">⚡</div>
                <div class="card-title">Direct Tally Prime Sync</div>
                <div class="card-desc">Synchronize complete financial history, balance sheet segments, and age books securely using standard XML endpoints.</div>
            </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
            <div class="landing-card">
                <div class="card-icon">🔒</div>
                <div class="card-title">Multi-Tenant Isolation</div>
                <div class="card-desc">Keep your client accounts separated. Client roles see only their assigned businesses, tables, and synced data history.</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    f4, f5, f6 = st.columns(3)
    with f4:
        st.markdown("""
            <div class="landing-card">
                <div class="card-icon">📄</div>
                <div class="card-title">Detailed MIS breakups</div>
                <div class="card-desc">Deep-dive into custom monthly breakups of P&L ledger details mapped automatically using ledgers configuration.</div>
            </div>
        """, unsafe_allow_html=True)
    with f5:
        st.markdown("""
            <div class="landing-card">
                <div class="card-icon">📅</div>
                <div class="card-title">Customer & Vendor Ageing</div>
                <div class="card-desc">Monitor accounts receivables and payables overdue intervals instantly. Filter by customer names and age brackets.</div>
            </div>
        """, unsafe_allow_html=True)
    with f6:
        st.markdown("""
            <div class="landing-card">
                <div class="card-icon">📥</div>
                <div class="card-title">Excel & PowerPoint Exports</div>
                <div class="card-desc">Export formatted financial spreadsheets or fully designed slide decks directly for your board meetings.</div>
            </div>
        """, unsafe_allow_html=True)

    # 4. Pricing Grid Section
    st.markdown('<h2 class="section-title">Flexible pricing plans</h2>', unsafe_allow_html=True)
    
    p1, p2, p3 = st.columns(3)
    
    with p1:
        st.markdown("""
            <div class="pricing-card">
                <div class="plan-name">Bronze Plan</div>
                <div class="plan-price">₹1,999<span>/mo</span></div>
                <ul class="plan-feature-list">
                    <li class="plan-feature-item">🟢 <b>Dashboard</b> page</li>
                    <li class="plan-feature-item">🟢 Basic P&L overview</li>
                    <li class="plan-feature-item">🟢 Format Excel exports</li>
                    <li class="plan-feature-item disabled">🔴 PowerPoint Exports</li>
                    <li class="plan-feature-item disabled">🔴 Cash Flow analysis</li>
                    <li class="plan-feature-item disabled">🔴 Auto Tally Sync</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Choose Bronze", key="p_bronze_btn"):
            st.session_state.onboarding_plan = "Bronze"
            st.session_state.onboarding_price = "₹1,999/mo"
            st.session_state.onboarding_features = ["dashboard", "downloads"]
            st.session_state.view = 'onboarding'
            st.rerun()
            
    with p2:
        st.markdown("""
            <div class="pricing-card popular">
                <div class="plan-name" style="color:#6366f1;">Silver Plan</div>
                <div class="plan-price">₹4,999<span>/mo</span></div>
                <ul class="plan-feature-list">
                    <li class="plan-feature-item">🟢 <b>Dashboard & Reports</b></li>
                    <li class="plan-feature-item">🟢 Detailed P&L breakup</li>
                    <li class="plan-feature-item">🟢 Customer & Vendor Ageing</li>
                    <li class="plan-feature-item">🟢 Excel & PPT downloads</li>
                    <li class="plan-feature-item disabled">🔴 Cash Flow analysis</li>
                    <li class="plan-feature-item">🟢 Manual Tally Sync</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Choose Silver", key="p_silver_btn", type="primary"):
            st.session_state.onboarding_plan = "Silver"
            st.session_state.onboarding_price = "₹4,999/mo"
            st.session_state.onboarding_features = ["dashboard", "reports", "downloads", "sync"]
            st.session_state.view = 'onboarding'
            st.rerun()
            
    with p3:
        st.markdown("""
            <div class="pricing-card">
                <div class="plan-name">Gold Plan</div>
                <div class="plan-price">₹9,999<span>/mo</span></div>
                <ul class="plan-feature-list">
                    <li class="plan-feature-item">🟢 <b>All Features</b> enabled</li>
                    <li class="plan-feature-item">🟢 Dashboard & Reports</li>
                    <li class="plan-feature-item">🟢 Cash Flow dashboards</li>
                    <li class="plan-feature-item">🟢 Unlimited Tally Sync</li>
                    <li class="plan-feature-item">🟢 Premium client portals</li>
                    <li class="plan-feature-item">🟢 Custom templates</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Choose Gold", key="p_gold_btn"):
            st.session_state.onboarding_plan = "Gold"
            st.session_state.onboarding_price = "₹9,999/mo"
            st.session_state.onboarding_features = ["dashboard", "reports", "cash_flow", "downloads", "sync"]
            st.session_state.view = 'onboarding'
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # 5. FAQs / Footer
    st.markdown("""
        <div style='text-align:center; padding: 40px 0 20px 0; color:#475569; font-size:0.8rem;'>
            <p>© 2026 MIS Portal SaaS. Secured with AES-256 and bcrypt credentials hashing.</p>
            <p style='margin-top:8px;'>Powering automated financial reports directly from Tally Prime ODBC configurations.</p>
        </div>
    """, unsafe_allow_html=True)
