"""Dashboard page — placeholder, full version coming next"""
import streamlit as st

def show_dashboard(user):
    st.title("📊 Dashboard")
    st.info("Dashboard loading... Full version coming soon.")
    st.json({
        "user": user.get('username'),
        "role": user.get('role'),
        "companies": user.get('company_ids', [])
    })
