import time
import pytz
import streamlit as st
from datetime import datetime
from datetime import time as dt_time

def render_add_tab(gs_manager):
    st.header("➕ New Drink")

    # SETUP & CONFIG
    types_df = gs_manager.get_beverage_types()
    config_df = gs_manager.get_config()
    
    user_tz_string = config_df.loc[config_df['Key'] == 'Timezone', 'Value'].values[0]
    local_tz = pytz.timezone(user_tz_string)
    now_dt = datetime.now(local_tz)

    # Initialize session state for sliders (to keep them stable)
    if "hour_slider" not in st.session_state:
        st.session_state.hour_slider = now_dt.hour
    if "min_slider" not in st.session_state:
        st.session_state.min_slider = now_dt.minute

    # TIME SELECTION (REACTIVE)
    st.subheader("When?")
    if st.button("⏰ Reset to Now", use_container_width=True):
        st.session_state.hour_slider = now_dt.hour
        st.session_state.min_slider = now_dt.minute
        st.rerun()

    date_val = st.date_input("Date", now_dt)
    selected_hour = st.select_slider(
        "Hour",
        options=list(range(24)),
        key="hour_slider",
        format_func=lambda x: f"{x:02d}"
    )
    selected_minute = st.select_slider(
        "Minute",
        options=list(range(60)),
        key="min_slider",
        format_func=lambda x: f"{x:02d}"
    )
    time_val = dt_time(selected_hour, selected_minute)

    # BEVERAGE SELECTION (REACTIVE)
    st.subheader("What?")
    types = types_df['Type'].dropna().unique().tolist()
    water_percentage = types_df.set_index('Type')['Water'].to_dict() if 'Water' in types_df.columns else {}
    default_cup = int(config_df.loc[config_df['Key'] == 'Default Cup Size (ml)', 'Value'].values[0])
    default_d2o = int(config_df.loc[config_df['Key'] == 'Default D2O Cup Size (ml)', 'Value'].values[0])

    col_bev, col_amt = st.columns(2)
    with col_bev:
        bev_type = st.selectbox("Beverage Type", options=types) # Changing this now triggers an immediate rerun, updating the amount
    current_default = default_d2o if "D2O" in bev_type else default_cup # Calculate dynamic default
    with col_amt:
        amount = st.number_input("Amount (ml)", min_value=0, step=10, value=current_default)

    note = st.text_area("Notes (Optional)", placeholder="Add a note here...")

    # CALCULATION PREVIEW (COOL UX FEATURE)
    percentage_str = water_percentage.get(bev_type, "100%")
    percentage_val = float(str(percentage_str).strip('%')) / 100
    calculated_water = int(amount * percentage_val)
    st.info(f"💧 This will add **{calculated_water}ml** of net water to your daily goal.")

    # SAVE BUTTON
    if st.button("🚀 Save Drink Entry", use_container_width=True, type="primary"):
        with st.spinner("Writing to Google Sheets..."):
            timestamp_str = datetime.combine(date_val, time_val).strftime("%Y-%m-%d %H:%M:%S")
            
            add_data = [
                timestamp_str,
                bev_type,
                amount,
                calculated_water,
                note
            ]
            
            # Save to Google Sheets
            gs_manager.add_log(add_data)
            
            # Success UI
            st.cache_data.clear()
            st.toast(f"Logged {amount}ml of {bev_type}!", icon="✅")
            st.balloons()

            # Switch tabs logic
            st.session_state.active_tab = "📋 Logs"
            st.session_state["pending_tab_switch"] = True
            time.sleep(1)
            st.rerun()