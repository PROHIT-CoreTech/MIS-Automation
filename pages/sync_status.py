"""Sync Status & Manual Trigger"""
import streamlit as st
from core.db import get_conn
from sync.tally_connect import test_connection
from sync.sync_engine import sync_all

def show_sync(user):
    st.title("🔄 Sync Status")

    # Tally connection status
    col1, col2 = st.columns([2,1])
    with col1:
        result = test_connection()
        if result['status'] == 'ok':
            st.success(f"✅ {result['message']}")
        else:
            st.error(f"❌ {result['message']}")
    with col2:
        if st.button("🔄 Sync All Companies Now", type="primary", use_container_width=True):
            with st.spinner("Syncing all companies from Tally..."):
                progress = st.empty()
                def cb(company, idx, total):
                    progress.info(f"Syncing {idx}/{total}: {company}")
                result = sync_all(progress_callback=cb)
            progress.empty()
            if result['status'] == 'ok':
                st.success(f"✅ Sync complete! {result['synced']}/{result['total']} companies synced.")
            else:
                st.error(f"Sync error: {result.get('message')}")
            st.rerun()

    st.divider()

    # Company sync status table
    st.subheader("Company Sync Status")
    conn = get_conn()
    companies = conn.execute("""
        SELECT tally_name, display_name, sync_status,
               last_sync, last_full_sync, is_active
        FROM companies ORDER BY display_name
    """).fetchall()
    conn.close()

    if not companies:
        st.info("No companies synced yet. Click 'Sync All Companies Now' to start.")
    else:
        for c in companies:
            status_icon = "🟢" if c['sync_status'] == 'ok' else ("🔴" if c['sync_status'] == 'error' else "⏳")
            col1, col2, col3, col4 = st.columns([3,2,2,1])
            with col1: st.write(f"{status_icon} {c['display_name'] or c['tally_name']}")
            with col2: st.caption(f"Last sync: {c['last_sync'] or 'Never'}")
            with col3: st.caption(f"Full sync: {c['last_full_sync'] or 'Never'}")
            with col4: st.caption("Active" if c['is_active'] else "Inactive")

    # Recent sync logs
    st.divider()
    st.subheader("Recent Sync Logs (Last 20)")
    conn = get_conn()
    logs = conn.execute("""
        SELECT sl.sync_type, sl.status, sl.records_synced,
               sl.error_msg, sl.ended_at, c.display_name
        FROM sync_log sl
        LEFT JOIN companies c ON c.id = sl.company_id
        ORDER BY sl.ended_at DESC LIMIT 20
    """).fetchall()
    conn.close()

    if not logs:
        st.info("No sync logs yet.")
    else:
        for log in logs:
            icon = "✅" if log['status'] == 'ok' else "❌"
            st.caption(
                f"{icon} {log['display_name'] or 'Unknown'} | "
                f"{log['sync_type']} | "
                f"{log['records_synced']} records | "
                f"{log['ended_at'] or ''} | "
                f"{log['error_msg'] or ''}"
            )
