import streamlit as st
import pandas as pd
import time

def render_config_tab(gs_manager):
    st.header("⚙️ Configuration")

    # --- SECTION 1: GENERAL SETTINGS ---
    with st.expander("👀 General Settings", expanded=True):
        config_df = gs_manager.get_config()
        
        # General settings usually has fixed keys, but we'll allow dynamic rows if you want to add new config keys
        edited_config = st.data_editor(
            config_df,
            num_rows="dynamic", 
            column_config={"Key": st.column_config.TextColumn("Setting Name")},
            hide_index=True,
            width="stretch",
            key="config_editor"
        )
        
        config_changes = st.session_state.get("config_editor", {})
        has_config_changes = any(config_changes.get(k) for k in ["edited_rows", "added_rows", "deleted_rows"])
        
        c1, c2 = st.columns([4, 1])
        if c2.button("Save Settings", key="btn_save_config", use_container_width=True, type="primary", disabled=not has_config_changes):
            gs_manager.update_config_sheet(edited_config)
            st.cache_data.clear()
            st.toast("General Settings updated!", icon="✅")
            time.sleep(1)
            st.rerun()

    # --- SECTION 2: BEVERAGE TYPES ---
    with st.expander("☕ Beverage Types", expanded=False):
        st.info("💡 Scroll to the bottom of the table and click (+) to add a new drink type.")
        types_df = gs_manager.get_beverage_types()
        
        edited_types = st.data_editor(
            types_df,
            num_rows="dynamic",
            hide_index=True,
            width="stretch",
            column_config={
                "Type": st.column_config.TextColumn("Drink Name", help="e.g. Latte"),
                "Water": st.column_config.TextColumn("Water %", help="e.g. 90%"),
                "Caffeine (mg)": st.column_config.NumberColumn("Caffeine", min_value=0, step=1)
            },
            key="types_editor"
        )
        
        type_changes = st.session_state.get("types_editor", {})
        has_type_changes = any(type_changes.get(k) for k in ["edited_rows", "added_rows", "deleted_rows"])
        
        c3, c4 = st.columns([4, 1])
        if c4.button("Save Types", key="btn_save_types", use_container_width=True, type="primary", disabled=not has_type_changes):
            gs_manager.update_beverage_types_sheet(edited_types)
            st.cache_data.clear()
            st.toast("Beverage Types updated!", icon="☕")
            time.sleep(1)
            st.rerun()
