"""
Dashboard — Pure Tally Group Logic
No Masters.xlsx dependency. Classification purely by Tally native group names.

Tally P&L Structure:
  TRADING ACCOUNT:
    Credit: Sales Accounts + Direct Incomes + Closing Stock
    Debit:  Opening Stock  + Purchase Accounts + Direct Expenses
    GP c/o = Credit - Debit

  P&L ACCOUNT:
    GP b/f + Indirect Incomes - Indirect Expenses = Nett Profit
"""
import streamlit as st
from datetime import date
from core.models    import PLData, BSData
from core.auth      import is_admin
from core.theme     import chart_layout, donut_chart_figure, CHART_COLORS, CHART_PALETTE
from core.constants import MONTHS, TALLY_MAP, COGS_NAMES, PL_HEADERS

def _is_skip(tg_l: str, mg_l: str) -> bool:
    """
    Skip true Tally section header rows and group total rows.
    Uses PL_HEADERS from core.constants.
    """
    if tg_l in PL_HEADERS or mg_l in PL_HEADERS:
        return True
    # Skip group total rows (tagged by fix_group_total.py)
    if mg_l == '_group_total_':
        return True
    return False


def _calc(rows):
    """
    Exact Tally P&L formula — matches Tally Prime P&L A/c exactly:

    TRADING ACCOUNT:
      Credit: Sales Accounts + Direct Incomes + Closing Stock
      Debit:  Opening Stock  + Purchase Accounts + Direct Expenses
      GP c/o = Credit - Debit

    P&L ACCOUNT:
      NP = GP b/f + Indirect Incomes - Indirect Expenses

    Group total rules (ledger_name == tally_group in Tally XML):
    - Sales Accounts group total    → USE for Revenue (accurate monthly total)
    - Cost of Sales : group total   → USE for COGS (Tally pre-calculated net)
    - Direct Incomes group total    → USE for Dir Inc (when items have 0 value)
    - Indirect Expenses group total → SKIP (use individual ledgers instead)
    - Indirect Incomes group total  → SKIP (use individual ledgers instead)
    """
    rev_total     = 0
    dir_inc_total = 0   # Direct Incomes group total
    dir_inc_items = 0   # Direct Incomes individual ledgers
    cos_net       = 0
    cos_net_found = False
    oh_grp        = 0   # Indirect Expenses group total (Tally pre-calculated)
    oh_grp_found  = False
    oh_sal_grp    = 0   # Salaries and Bonus group total (separate Tally group)
    oh_sal_found  = False
    oh_items      = 0   # Individual overhead ledgers (fallback)
    ind_inc       = 0
    b = {k: 0 for k in ('opening', 'purchases', 'direct_exp', 'closing')}

    for r in rows:
        tg  = str(r['tally_group']  or '').lower().strip()
        mg  = str(r['mis_group']    or '').lower().strip()
        ln  = str(r['ledger_name']  or '').lower().strip()
        val     = abs(r['net'] or 0)   # for income/expense items
        net_val = r['net'] or 0         # for COGS (can be +/- per month)

        # ── INDIRECT EXPENSES group total — capture BEFORE skip rules ──
        if tg == 'indirect expenses' and ln == 'indirect expenses':
            oh_grp       += net_val
            oh_grp_found  = True
            continue

        # ── SALARIES AND BONUS group total — capture BEFORE skip rules ──
        if tg == 'salaries and bonus' and ln == 'salaries and bonus':
            oh_sal_grp   += net_val
            oh_sal_found  = True
            continue

        if _is_skip(tg, mg):
            continue

        # Skip other group total rows
        if ln == tg and tg not in ('sales accounts', 'cost of sales :',
                                   'direct incomes'):
            continue

        # ── SALES ACCOUNTS ───────────────────────────────
        # NOTE: previously this only counted a row if mg == 'sales
        # accounts', which in practice ONLY matched the group-total
        # row itself (ledger_name == tally_group). Individual sales
        # ledgers (e.g. 'EXPORT SALES', 'GST SALES', 'IGST SALES')
        # get their OWN specific mis_group from Masters.xlsx, so they
        # were silently excluded from Revenue entirely.
        #
        # The sync parser (parse_pl_xml) does not emit a group-total
        # row for 'Sales Accounts' at all — only individual member
        # ledgers under it — so any group-total row present in the DB
        # is a stale leftover that will never be refreshed again.
        # Summing every individual ledger under 'sales accounts'
        # (and explicitly excluding a group-total row if one is ever
        # present, to avoid double-counting) is what actually stays
        # live and matches Tally's own P&L going forward.
        if tg == 'sales accounts':
            if ln != tg:
                rev_total += net_val
            continue

        # ── DIRECT INCOMES ────────────────────────────────
        if tg == 'direct incomes':
            if mg == 'direct incomes':
                dir_inc_total += net_val
            else:
                dir_inc_items += val
            continue

        # ── COST OF SALES — use net (not abs) ────────────
        # Monthly COGS can flip sign; annual SUM(net) = correct COGS
        if tg == 'cost of sales :':
            cos_net       += net_val
            cos_net_found  = True
            continue

        # ── INDIRECT INCOMES ──────────────────────────────
        if tg == 'indirect incomes':
            ind_inc += val
            continue

        # ── INDIRECT EXPENSES individual ledgers (fallback) ──
        if tg in ('indirect expenses', 'salaries and bonus', 'salary accounts'):
            oh_items += val
            continue

        # ── COGS individual groups (Mode B fallback) ─────
        if tg == 'opening stock':                            b['opening']   += val
        elif tg in ('purchase accounts',
                    'add: purchase accounts'):               b['purchases'] += val
        elif tg == 'direct expenses':                        b['direct_exp']+= val
        elif tg in ('less: closing stock', 'closing stock'): b['closing']   += val

    # Direct Incomes: group total preferred
    dir_inc   = abs(dir_inc_total) if dir_inc_total else abs(dir_inc_items)

    # COGS: group total preferred (Mode A), fallback to individual groups
    if cos_net_found:
        cogs = abs(cos_net)
    else:
        cogs = b['opening'] + b['purchases'] + b['direct_exp'] - b['closing']

    # Overhead: IE group total + Salaries group total (both Tally pre-calculated)
    # Fallback to individual sum if group totals not found
    if oh_grp_found or oh_sal_found:
        overhead = abs(oh_grp) + abs(oh_sal_grp)
    else:
        overhead = oh_items

    rev_total = abs(rev_total)
    gp     = rev_total + dir_inc - cogs
    np_    = gp + ind_inc - overhead
    gp_pct = round(gp  / rev_total * 100, 1) if rev_total else 0
    np_pct = round(np_ / rev_total * 100, 1) if rev_total else 0

    return dict(revenue=rev_total, dir_inc=dir_inc, cogs=cogs,
                gp=gp, gp_pct=gp_pct, ind_inc=ind_inc,
                overhead=overhead, np=np_, np_pct=np_pct)


def _monthly(rows):
    """Monthly breakdown for charts."""
    from collections import defaultdict
    buckets = defaultdict(list)
    for r in rows:
        yr  = int(r['year'])
        mo  = int(r['month'])
        lbl = r['month_label'] or f"{MONTHS[mo-1]}-{str(yr)[2:]}"
        buckets[(yr, mo, lbl)].append(r)
    result = []
    for key in sorted(buckets):
        p = _calc(buckets[key])
        result.append({'year': key[0], 'month': key[1],
                       'month_label': key[2], **p})
    return result


def show_dashboard(user):

    # ── Read from shared sidebar filter (set by app.py) ──────
    company_id   = st.session_state.get('global_company_id')
    company_name = st.session_state.get('global_company_name', '')
    from_lbl     = st.session_state.get('global_from_lbl')
    to_lbl       = st.session_state.get('global_to_lbl')
    from_yr      = st.session_state.get('global_from_yr')
    from_mo      = st.session_state.get('global_from_mo')
    to_yr        = st.session_state.get('global_to_yr')
    to_mo        = st.session_state.get('global_to_mo')

    if not company_id or not from_lbl:
        st.info("Select a company and date range from the sidebar to view the dashboard.")
        return

    # Available months for n_months count
    from core.db import get_available_months
    avail = get_available_months(company_id)

    if not avail:
        st.info("No data synced yet. Please sync from Tally first.")
        return

    n_months = sum(1 for y, m in avail
                   if (y, m) >= (from_yr, from_mo)
                   and (y, m) <= (to_yr, to_mo))

    # ── STICKY HEADER — stays visible while scrolling charts below ──
    st.markdown(f"""
        <div class="page-sticky-header">
            <div class="page-title-row">📊 Management Dashboard</div>
            <div class="page-company-row">🏢 {company_name}</div>
        </div>
    """, unsafe_allow_html=True)
    st.caption(f"📅 {from_lbl} → {to_lbl} &nbsp;|&nbsp; {n_months} months",
               unsafe_allow_html=True)
    st.markdown("---")

    # ── FETCH ──────────────────────────────────────────────
    pl_data_docs = PLData.objects(company=company_id).order_by('year', 'month')
    bs_data_docs = BSData.objects(company=company_id).order_by('year', 'month')

    pl_rows = []
    for doc in pl_data_docs:
        if ((doc.year > from_yr) or (doc.year == from_yr and doc.month >= from_mo)) and \
           ((doc.year < to_yr) or (doc.year == to_yr and doc.month <= to_mo)):
           pl_rows.append({
               'ledger_name': doc.ledger_name,
               'mis_group': doc.mis_group,
               'tally_group': doc.tally_group,
               'year': doc.year,
               'month': doc.month,
               'month_label': doc.month_label,
               'net': doc.net
           })
           
    bs_rows = []
    for doc in bs_data_docs:
        if ((doc.year > from_yr) or (doc.year == from_yr and doc.month >= from_mo)) and \
           ((doc.year < to_yr) or (doc.year == to_yr and doc.month <= to_mo)):
           bs_rows.append({
               'ledger_name': doc.ledger_name,
               'year': doc.year,
               'month': doc.month,
               'closing_bal': doc.closing_bal
           })

    if not pl_rows:
        st.info("No P&L data for selected period.")
        return

    import plotly.express as px
    import plotly.graph_objects as go

    # ── CALCULATE ──────────────────────────────────────────
    p       = _calc(pl_rows)
    monthly = _monthly(pl_rows)

    # Cash & Bank from BS (latest month)
    cash_total = fa_total = 0
    for r in bs_rows:
        if int(r['year']) == to_yr and int(r['month']) == to_mo:
            n = str(r['ledger_name'] or '').lower()
            v = abs(r['closing_bal'] or 0)
            if 'bank account' in n or 'cash-in-hand' in n:
                cash_total += v
            if any(k in n for k in ['plant','machinery','building',
                                     'equipment','furniture','computer','land']):
                fa_total += v

    ctype = ('PRE_REVENUE' if p['revenue'] == 0 and fa_total > 0
             else 'OPERATING' if p['revenue'] > 0 else 'STANDARD')

    def fmt(v):
        a = abs(v); s = '-' if v < 0 else ''
        if a >= 1e7:   return f"{s}₹{a/1e7:.2f} Cr"
        elif a >= 1e5: return f"{s}₹{a/1e5:.1f} L"
        else:          return f"{s}₹{a:,.0f}"

    # ── KPI CARDS ──────────────────────────────────────────
    if ctype == 'OPERATING':
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("📈 Revenue",      fmt(p['revenue']))
        c2.metric("💹 Gross Profit", fmt(p['gp']),
                  delta=f"{p['gp_pct']:.1f}%",
                  delta_color="normal" if p['gp'] > 0 else "inverse")
        c3.metric("💰 Net Profit",   fmt(p['np']),
                  delta=f"{p['np_pct']:.1f}%",
                  delta_color="normal" if p['np'] > 0 else "inverse")
        c4.metric("🏦 Cash & Bank",  fmt(cash_total))
        c5.metric("💸 Overhead",     fmt(p['overhead']))
    elif ctype == 'PRE_REVENUE':
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("🏗️ Capex",        fmt(fa_total))
        c2.metric("💸 Overhead",     fmt(p['overhead']))
        c3.metric("🏦 Cash & Bank",  fmt(cash_total))
        burn = p['overhead'] / n_months if n_months else 1
        rnwy = cash_total / burn if burn else 0
        c4.metric("⏱️ Cash Runway", f"{rnwy:.1f} months",
                  delta="⚠️ Low" if rnwy < 3 else "✅ OK",
                  delta_color="inverse" if rnwy < 3 else "normal")
    else:
        c1,c2,c3 = st.columns(3)
        c1.metric("🏦 Cash & Bank",  fmt(cash_total))
        c2.metric("💸 Overhead",     fmt(p['overhead']))
        c3.metric("📊 Net Position", fmt(p['np']))

    st.markdown("---")

    # ── CHARTS ─────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-card"><p class="chart-title">📈 Revenue vs Profit Trend</p>',
                    unsafe_allow_html=True)
        if monthly and any(m['revenue'] for m in monthly):
            lbs = [m['month_label'] for m in monthly]
            rev_vals = [m['revenue'] for m in monthly]
            # Distinct color per bar (cycled) — makes month-to-month
            # comparison easier to read than one flat colour.
            bar_colors = [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(len(lbs))]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=lbs, y=rev_vals, name='Revenue',
                marker=dict(
                    color=bar_colors,
                    line=dict(color='rgba(255,255,255,0.08)', width=1),
                    opacity=0.88,
                ),
            ))
            # Highlight cap line
            fig.add_trace(go.Scatter(
                x=lbs, y=rev_vals, mode='markers', name='',
                marker=dict(symbol='line-ew', size=18,
                            line=dict(width=3, color='rgba(255,255,255,0.4)')),
                showlegend=False, hoverinfo='skip',
            ))
            fig.add_trace(go.Scatter(x=lbs, y=[m['gp'] for m in monthly],
                name='Gross Profit', mode='lines+markers',
                line=dict(color=CHART_COLORS['emerald'], width=2.5),
                marker=dict(size=5, color=CHART_COLORS['emerald'])))
            fig.add_trace(go.Scatter(x=lbs, y=[m['np'] for m in monthly],
                name='Net Profit', mode='lines+markers',
                line=dict(color=CHART_COLORS['sky'], width=2.5, dash='dot'),
                marker=dict(size=5, color=CHART_COLORS['sky'])))
            chart_layout(fig, height=300,
                        legend=dict(orientation='h', yanchor='bottom', y=1.02,
                                    font=dict(color=CHART_COLORS['text'], size=10)))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-card"><p class="chart-title">💸 Overhead Breakdown</p>',
                    unsafe_allow_html=True)
        oh_grp = {}
        for r in pl_rows:
            tg = str(r['tally_group'] or '').lower().strip()
            mg = str(r['mis_group']   or '').lower().strip()
            if tg in ('indirect expenses','salaries and bonus','salary accounts'):
                if not _is_skip(tg, mg):
                    lbl = r['mis_group'] or r['tally_group']
                    oh_grp[lbl] = oh_grp.get(lbl, 0) + abs(r['net'] or 0)
        oh_grp = {k:v for k,v in oh_grp.items() if v > 0}
        if oh_grp:
            fig2 = donut_chart_figure(list(oh_grp.keys()), list(oh_grp.values()))
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No overhead data")
        st.markdown('</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="chart-card"><p class="chart-title">🏦 Cash &amp; Bank Trend</p>',
                    unsafe_allow_html=True)
        ct = {}
        for r in bs_rows:
            n = str(r['ledger_name'] or '').lower()
            if 'bank account' in n or 'cash-in-hand' in n:
                k = (int(r['year']), int(r['month']))
                ct[k] = ct.get(k, 0) + abs(r['closing_bal'] or 0)
        if ct:
            items = sorted(ct.items())
            xs = [f"{MONTHS[k[0][1]-1]}-{str(k[0][0])[2:]}" for k in items]
            ys = [v for _,v in items]
            fig3 = go.Figure(go.Scatter(
                x=xs, y=ys, mode='lines', fill='tozeroy',
                line=dict(color=CHART_COLORS['blue'], width=2.5),
                fillcolor='rgba(46,155,231,0.18)',
            ))
            chart_layout(fig3, height=280, showlegend=False)
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No cash/bank data")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="chart-card"><p class="chart-title">📊 GP% vs NP% Trend</p>',
                    unsafe_allow_html=True)
        if monthly and any(m['revenue'] for m in monthly):
            lbs = [m['month_label'] for m in monthly]
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(x=lbs, y=[m['gp_pct'] for m in monthly],
                name='GP%', mode='lines+markers',
                line=dict(color=CHART_COLORS['mint'],width=2), marker=dict(size=5)))
            fig4.add_trace(go.Scatter(x=lbs, y=[m['np_pct'] for m in monthly],
                name='NP%', mode='lines+markers',
                line=dict(color=CHART_COLORS['violet'],width=2,dash='dot'), marker=dict(size=5)))
            fig4.add_hline(y=0, line_dash='dash', line_color='rgba(255,255,255,0.25)', opacity=0.6)
            chart_layout(fig4, height=280,
                        legend=dict(orientation='h', font=dict(color=CHART_COLORS['text'], size=10)),
                        yaxis=dict(gridcolor=CHART_COLORS['grid'], color=CHART_COLORS['text'],
                                    ticksuffix='%'))
            st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No revenue data for trend")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── INSIGHTS ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💡 Key Insights")

    insights = []
    if ctype == 'OPERATING':
        gp_pct = p['gp_pct']; np_pct = p['np_pct']
        rev    = p['revenue']; oh     = p['overhead']

        if gp_pct > 25:
            insights.append(('success','✅','Strong Gross Margin',
                             f'GP% {gp_pct:.1f}% — healthy profitability'))
        elif gp_pct > 10:
            insights.append(('info','ℹ️','Moderate Gross Margin',
                             f'GP% {gp_pct:.1f}% — room to improve'))
        else:
            insights.append(('error','🔴','Low Gross Margin',
                             f'GP% only {gp_pct:.1f}% — review pricing and COGS'))

        if p['np'] < 0:
            insights.append(('error','🔴','Net Loss',
                             f'Loss of {fmt(abs(p["np"]))} — overhead exceeding GP'))
        elif np_pct > 10:
            insights.append(('success','✅','Profitable',
                             f'Net profit {fmt(p["np"])} ({np_pct:.1f}%)'))
        else:
            insights.append(('warning','⚠️','Thin Margin',
                             f'NP% {np_pct:.1f}% — monitor overhead'))

        if rev > 0:
            oh_r = oh / rev * 100
            if oh_r > 30:
                insights.append(('warning','⚠️','High Overhead',
                                 f'Overhead {oh_r:.1f}% of revenue'))
            else:
                insights.append(('success','✅','Overhead Lean',
                                 f'Overhead {oh_r:.1f}% of revenue'))

    elif ctype == 'PRE_REVENUE':
        burn = p['overhead'] / n_months if n_months else 1
        rnwy = cash_total / burn if burn else 0
        if rnwy < 3:
            insights.append(('error','🔴','Critical Cash Runway',
                             f'Only {rnwy:.1f} months at {fmt(burn)}/month'))
        else:
            insights.append(('info','ℹ️','Pre-Revenue',
                             f'{rnwy:.1f} months cash runway'))
        if fa_total:
            insights.append(('success','✅','Capex Deployed',
                             f'Fixed assets {fmt(fa_total)}'))

    cm = {
        'success': ('rgba(16,185,129,0.12)', '#6ee7b7', 'rgba(16,185,129,0.6)'),
        'warning': ('rgba(251,191,36,0.10)',  '#fde68a', 'rgba(251,191,36,0.5)'),
        'error':   ('rgba(244,63,94,0.12)',   '#fda4af', 'rgba(244,63,94,0.5)'),
        'info':    ('rgba(99,102,241,0.12)',   '#a5b4fc', 'rgba(99,102,241,0.5)'),
    }
    for itype, icon, title, detail in insights:
        bg, fg, bd = cm.get(itype, cm['info'])
        st.markdown(f"""
            <div style="background:{bg};color:{fg};border-left:3px solid {bd};
                border: 1px solid {bd.replace('0.5','0.2').replace('0.6','0.2')};
                border-left: 3px solid {bd};
                padding:0.75rem 1rem;border-radius:12px;margin-bottom:0.5rem;
                backdrop-filter:blur(10px);">
                <strong style="color:{fg}">{icon} {title}</strong><br>
                <span style="font-size:0.88rem;color:{fg};opacity:0.8">{detail}</span>
            </div>""", unsafe_allow_html=True)
