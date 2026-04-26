import streamlit as st
from google_sheets import SpreadsheetManager
from tabs.add_tab import render_add_tab
from tabs.logs_tab import render_logs_tab
from tabs.config_tab import render_config_tab

st.set_page_config(page_title="Liquid Tracker", page_icon="💧")

# Initialize Session State for the Spreadsheet Manager (Prevents re-auth on every click)
if 'gs' not in st.session_state:
    sheet_name = st.secrets["gsheets"]["sheet_name"]
    manager = SpreadsheetManager(st.secrets["gcp_service_account"], sheet_name)
    # st.session_state.gs = SpreadsheetManager("credentials.json", "Liquid Tracker")

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
        logs_df = st.session_state.gs.get_logs() 
    render_logs_tab(st.session_state.gs, logs_df)
elif st.session_state.active_tab == "➕ New Drink":
    render_add_tab(st.session_state.gs)
elif st.session_state.active_tab == "⚙️ Config":
    render_config_tab(st.session_state.gs)