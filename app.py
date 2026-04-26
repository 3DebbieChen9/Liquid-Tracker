import streamlit as st
from google_sheets import SpreadsheetManager
from tabs.add_tab import render_add_tab
from tabs.logs_tab import render_logs_tab
from tabs.config_tab import render_config_tab

st.set_page_config(page_title="Liquid Tracker", page_icon="💧")

# Initialize Session State for the Spreadsheet Manager (Prevents re-auth on every click)
if 'gs_manager' not in st.session_state:
    with st.spinner("Connecting to Google Sheets..."):
        st.session_state.gs_manager = SpreadsheetManager()

gs_manager = st.session_state.gs_manager

# 1. This variable controls which "Tab" is highlighted
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "📋 Logs"

# 2. Create the "Fake Tabs" using Segmented Control
# This looks like tabs but allows us to programmatically change it

# Only sync the widget when a programmatic tab switch was requested
if st.session_state.get("pending_tab_switch"):
    st.session_state["nav_widget"] = st.session_state.active_tab
    st.session_state["pending_tab_switch"] = False

nav_option = st.segmented_control(
    label="Navigation",
    options=["📋 Logs", "➕ New Drink", "⚙️ Config"],
    selection_mode="single",
    key="nav_widget",
    label_visibility="collapsed"
)
# Default Tab is "📋 Logs"
if "nav_widget" not in st.session_state:
    st.session_state["nav_widget"] = "📋 Logs"

# 3. Update our tracker if the user manually clicks
if nav_option:
    st.session_state.active_tab = nav_option

# 4. Render based on active_tab
if st.session_state.active_tab == "📋 Logs":
    with st.spinner("Refreshing logs..."):
        logs_df = st.session_state.gs_manager.get_logs()
    render_logs_tab(st.session_state.gs_manager, logs_df)
elif st.session_state.active_tab == "➕ New Drink":
    render_add_tab(st.session_state.gs_manager)
elif st.session_state.active_tab == "⚙️ Config":
    render_config_tab(st.session_state.gs_manager)