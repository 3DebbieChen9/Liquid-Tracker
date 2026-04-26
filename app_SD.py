import streamlit as st
from google_sheets_SD import SpreadsheetManager
from tabs.add_tab_SD import render_add_tab
from tabs.logs_tab_SD import render_logs_tab
from tabs.config_tab_SD import render_config_tab

st.set_page_config(page_title="Liquid Tracker - Stan", page_icon="💧")
st.markdown("<h1 style='text-align: center; color: #3128a7;'>💧 Liquid Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.8;'>Stay hydrated, stay healthy, Stan!</p>", unsafe_allow_html=True)

# Controls which "Tab" is highlighted
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "📋 Logs"
if st.session_state.get("pending_tab_switch"):
    st.session_state["nav_widget"] = st.session_state.active_tab
    st.session_state["pending_tab_switch"] = False

nav_option = st.segmented_control(
    label="Navigation",
    options=["📋 Logs", "➕ New Drink", "⚙️ Config"],
    selection_mode="single",
    key="nav_widget",
    label_visibility="collapsed",
    width="stretch"
)

# Initialize Session State for the Spreadsheet Manager (Prevents re-auth on every click)
if 'gs_manager' not in st.session_state:
    with st.spinner("Connecting to Google Sheets..."):
        st.session_state.gs_manager = SpreadsheetManager()

gs_manager = st.session_state.gs_manager

# Default Tab is "📋 Logs"
if "nav_widget" not in st.session_state:
    st.session_state["nav_widget"] = "📋 Logs"

# Update tracke nav_tab option if the user manually clicks
if nav_option:
    st.session_state.active_tab = nav_option

# Render based on active_tab
if st.session_state.active_tab == "📋 Logs":
    with st.spinner("Refreshing logs..."):
        logs_df = st.session_state.gs_manager.get_logs()
    render_logs_tab(st.session_state.gs_manager, logs_df)
elif st.session_state.active_tab == "➕ New Drink":
    render_add_tab(st.session_state.gs_manager)
elif st.session_state.active_tab == "⚙️ Config":
    render_config_tab(st.session_state.gs_manager)