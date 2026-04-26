import streamlit as st
from datetime import datetime
from streamlit_extras.no_default_selectbox import find_selected_working_day
import time
import pytz

def render_add_tab(gs_manager):
    st.header("➕ New Drink")

    types_df = gs_manager.get_beverage_types()
    sources_df = gs_manager.get_beverage_sources()
    config_df = gs_manager.get_config()
    
    user_tz_string = config_df.loc[config_df['Key'] == 'Timezone', 'Value'].values[0]
    local_tz = pytz.timezone(user_tz_string)

    types = types_df['Type'].dropna().unique().tolist()
    sources = sources_df['Source'].dropna().unique().tolist()
    water_percentage = types_df.set_index('Type')['Water'].to_dict() if 'Water' in types_df.columns else {}
    default_cup_size = config_df.loc[config_df['Key'] == 'Default Cup Size (ml)', 'Value'].values[0] if not config_df.empty else 250

    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_val = col1.date_input("Date", datetime.now(local_tz))
        time_val = col2.time_input("Time", datetime.now(local_tz), step = 60)
        
        col3, col4 = st.columns(2)
        bev_type = col3.selectbox("Beverage Type", options=types)
        amount = col4.number_input("Amount (ml)", min_value=0, step=50, value=default_cup_size)
        
        col5, col6 = st.columns(2)
        bev_source = col5.selectbox("Source", options=sources)
        price = col6.number_input("Price ($NTD)", min_value=0, step=5, value=0)
        
        note = st.text_area("Notes")
        
        if st.form_submit_button("Save Drink", use_container_width=True):
            timestamp_str = datetime.combine(date_val, time_val).strftime("%Y-%m-%d %H:%M:%S")
            water_amount = int(amount * float(water_percentage.get(bev_type, "100%").strip('%')) / 100)
            add_data = [
                timestamp_str,
                bev_type,
                amount,
                water_amount,
                note,
                bev_source,
                price
            ]
            gs_manager.add_log(add_data)
            st.cache_data.clear()
            st.toast("Successfully logged!", icon="✅")
            st.balloons()

            st.session_state.active_tab = "📋 Logs"
            st.session_state["pending_tab_switch"] = True
            time.sleep(1)
            st.rerun()   