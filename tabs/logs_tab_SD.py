import streamlit as st
import pandas as pd
from datetime import datetime
import time
import pytz

def render_logs_tab(gs_manager, df):
    st.header("📋 Activity Logs")
    
    # 1. Fetch data
    config_df = gs_manager.get_config()
    user_tz_string = config_df.loc[config_df['Key'] == 'Timezone', 'Value'].values[0]
    local_tz = pytz.timezone(user_tz_string)

    if df.empty:
        st.info("👀 No logs found yet. Go to the 'Add' tab to log your first drink!")
        return

    # --- PROGRESS BAR LOGIC ---
    daily_goal = config_df.loc[config_df['Key'] == 'Daily Goal (ml)', 'Value'].values[0] if not config_df.empty else 2000
    
    # 1. Convert the single column to datetime objects safely
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    # 2. Sort by that column
    df = df.sort_values(by='Timestamp', ascending=False)
    
    # Get today's date as a date object (normalized to midnight)
    today_date = datetime.now(local_tz).date()
    
    # --- FILTERING ---
    # Use .dt.date to compare only the date part, ignoring the time
    today_df = df[df['Timestamp'].dt.date == today_date]
    current_intake = today_df['Water Amount (ml)'].sum()

    # Calculate percentage (0.0 to 1.0)
    progress_percentage = min(current_intake / daily_goal, 1.0)
    
    # UI Display
    col1, col2 = st.columns([3, 1])
    col1.write(f"🎯 Daily Goal Progress: {current_intake}ml / {daily_goal}ml")
    
    # Change color based on progress (Logic for metric)
    status_color = "normal" if current_intake < daily_goal else "inverse"
    col2.metric("Status", f"{int(progress_percentage * 100)}%", delta_color=status_color)
    
    # The Progress Bar
    st.progress(progress_percentage)
    
    if progress_percentage >= 1.0:
        st.success("🙌 Target Reached! You're fully hydrated! 🌊")
    
    st.divider()
    
    # This enables a radio-button column on the left
    event = st.dataframe(
        df,
        width="stretch",
        hide_index=True, # Keeping index helps map back to the spreadsheet
        on_select="rerun", # This tells Streamlit to refresh when a row is clicked
        selection_mode="single-row",
        column_config={
            "Timestamp": st.column_config.DatetimeColumn(
                "Timestamp",
                format="YYYY-MM-DD HH:mm"
            ),
            "Amount (ml)": st.column_config.NumberColumn(
                "Amount",
                format="%d ml"
            ),
            "Water Amount (ml)": st.column_config.NumberColumn(
                "Water",
                format="%d ml"
            )
        }
    )

    selected_rows = event.selection.rows
    
    if selected_rows:
        # Get the actual index from the DataFrame based on the selection
        # Since the DF is sorted, we use .iloc to get the right data
        selected_idx = selected_rows[0]
        row_data = df.iloc[selected_idx]
        
        # 3. Display the Edit Form in an Expander or Container
        st.divider()
        with st.expander(f"📝 Editing: {row_data['Beverage Type']} at {row_data['Timestamp'].strftime('%H:%M')}", expanded=True):
            render_edit_form(gs_manager, row_data, row_data.name)
    else:
        st.info("💡 Tap the circle next to a row to edit that entry.")


def render_edit_form(gs_manager, row_data, sheet_row):
    # Fetch dropdown options
    types_df = gs_manager.get_beverage_types()
    
    types = types_df['Type'].tolist()
    water_percentage = types_df.set_index('Type')['Water'].to_dict() if 'Water' in types_df.columns else {}

    with st.form("edit_form"):
        u_timestamp = st.datetime_input(
            "Timestamp",
            row_data['Timestamp']
        )
        col3, col4 = st.columns(2)
        u_type = col3.selectbox("Type", options=types, index=types.index(row_data['Beverage Type']))
        u_amount = col4.number_input("Amount (ml)", value=int(row_data['Amount (ml)']), step=50)
        u_note = st.text_area("Notes", value=row_data['Notes'])

        col_update, col_delete = st.columns([1, 1])
        
        # UPDATE BUTTON
        if col_update.form_submit_button("Update Entry", use_container_width=True, type="primary"):
            new_ts = u_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            u_water_amount = int(u_amount * float(water_percentage.get(u_type, "100%").strip('%')) / 100)
            # Prepare data for Google Sheets
            updated_row = [
                new_ts, u_type, u_amount, u_water_amount, u_note
            ]

            gs_manager.update_log(sheet_row, updated_row)
            st.cache_data.clear()
            st.toast("Updated!", icon="🔄")
            time.sleep(1)
            st.rerun()

        # DELETE BUTTON
        if col_delete.form_submit_button("Delete Entry", use_container_width=True):
            gs_manager.delete_log(sheet_row)
            st.cache_data.clear()
            st.toast("Entry deleted", icon="🗑️")
            time.sleep(1)
            st.rerun()