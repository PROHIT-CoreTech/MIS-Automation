"""Downloads page — placeholder"""
import streamlit as st
from core.auth import can_download_excel, can_download_ppt

def show_downloads(user):
    st.title("📥 Downloads")
    col1, col2 = st.columns(2)
    with col1:
        if can_download_excel(user):
            st.button("📗 Download Excel Report", use_container_width=True, type="primary")
        else:
            st.info("Excel download not enabled for your account.")
    with col2:
        if can_download_ppt(user):
            st.button("📑 Download PPT Report", use_container_width=True, type="primary")
        else:
            st.info("PPT download not enabled for your account.")
