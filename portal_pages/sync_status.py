"""Sync Status — Auto fetch companies + Sync"""
import streamlit as st
import requests
import re
from core.db import get_conn

TALLY_URL = "http://localhost:9000"

def test_tally():
    try:
        r = requests.post(TALLY_URL,
            data='<ENVELOPE><HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER></ENVELOPE>',
            headers={'Content-Type': 'application/xml'}, timeout=10)
        return r.status_code == 200
    except:
        return False

def show_sync(user):
    st.markdown("## 🔄 Sync Status")

    # Connection check
    if test_tally():
        st.success("✅ Tally connected successfully")
    else:
        st.error("❌ Tally not connected — open Tally with a company")
        return

    st.divider()

    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown("### Sync Data from Tally")
        st.caption("This will fetch all companies from Tally and sync their data to the portal.")
    with col2:
        sync_btn = st.button("🔄 Sync Now", type="primary", use_container_width=True)

    if sync_btn:
        from sync.sync_engine import sync_all
        status   = st.empty()
        progress = st.progress(0)

        def cb(company, idx, total):
            progress.progress(idx/total)
            status.info(f"⏳ Syncing **{company}** ({idx}/{total})")

        with st.spinner("Connecting to Tally..."):
            result = sync_all(progress_callback=cb, tenant_id=user.get('tenant_id', 1))

        progress.progress(1.0)

        if result['status'] == 'ok':
            status.success(
                f"✅ Sync complete! "
                f"**{result['synced']}/{result['total']}** companies synced."
            )
            if result.get('results'):
                for r in result['results']:
                    if r['status'] == 'ok':
                        st.write(f"  🟢 {r['company']} — {r.get('records',0)} records")
                    else:
                        st.write(f"  🔴 {r['company']} — {r.get('error','unknown error')}")
        else:
            status.error(f"❌ {result.get('message','Sync failed')}")

        st.rerun()

    st.divider()
    st.markdown("### Company Sync Status")
    conn = get_conn()
    cos  = conn.execute("""
        SELECT tally_name, sync_status, last_sync, last_full_sync
        FROM companies 
        WHERE tenant_id = ?
        ORDER BY tally_name
    """, (user.get('tenant_id', 1),)).fetchall()
    conn.close()

    if not cos:
        st.info("No companies synced yet. Click **🔄 Sync Now** above.")
    else:
        for c in cos:
            icon = ("🟢" if c['sync_status']=='ok'
                    else "🔴" if c['sync_status']=='error' else "⏳")
            col1, col2 = st.columns([4,2])
            col1.write(f"{icon} **{c['tally_name']}**")
            col2.caption(c['last_sync'] or 'Never')
