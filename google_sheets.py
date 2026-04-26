import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

class SpreadsheetManager:
    def __init__(_self):
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["gcp_service_account"], 
            scope
        )
        _self.client = gspread.authorize(creds)
        _self.workbook = _self.client.open(st.secrets["gsheets"]["sheet_name"])
        _self.log_sheet = _self.workbook.worksheet("Logs")
        _self.beveragetypes_sheet = _self.workbook.worksheet("BeverageTypes")
        _self.beveragesource_sheet = _self.workbook.worksheet("BeverageSources")
        _self.config_sheet = _self.workbook.worksheet("Configuration")

    @st.cache_data(ttl=300) # Caches data for 5 minutes (300 seconds)
    def get_logs(_self):
        _self.log_sheet = _self.workbook.worksheet("Logs")
        return pd.DataFrame(_self.log_sheet.get_all_records())
    
    @st.cache_data(ttl=600)
    def get_beverage_types(_self):
        _self.beveragetypes_sheet = _self.workbook.worksheet("BeverageTypes")
        return pd.DataFrame(_self.beveragetypes_sheet.get_all_records())

    @st.cache_data(ttl=600)
    def get_beverage_sources(_self):
        _self.beveragesource_sheet = _self.workbook.worksheet("BeverageSources")
        return pd.DataFrame(_self.beveragesource_sheet.get_all_records())

    @st.cache_data(ttl=600)
    def get_config(_self):
        _self.config_sheet = _self.workbook.worksheet("Configuration")
        return pd.DataFrame(_self.config_sheet.get_all_records())

    def add_log(_self, row):
        _self.log_sheet.append_row(row)
        _self.sort_logs() # Sort after adding

    def update_log(_self, row_index, updated_row):
        # gspread uses 1-based indexing; row 1 is headers, so we add 2 to the 0-based dataframe index
        _self.log_sheet.update(f'A{row_index+2}:H{row_index+2}', [updated_row])
        _self.sort_logs() # Sort after adding

    def delete_log(_self, row_number):
        """Deletes a specific row from the Logs sheet."""
        _self.log_sheet.delete_rows(row_number + 2) # +2 because of 1-based indexing and header row

    def sort_logs(_self):
        """Sorts the Google Sheet by Timestamp (Col A)"""
        # 0 is column A
        # Order: 'ASCENDING' or 'DESCENDING'
        _self.log_sheet.sort((1, 'des'))

    def update_config_sheet(_self, df):
        # Convert DF back to list of lists including header
        data = [df.columns.values.tolist()] + df.values.tolist()
        _self.config_sheet.update('A1', data)

    def update_beverage_types_sheet(_self, df):
        # This takes the fresh dataframe (with new rows) and overwrites the sheet
        # 1. Prepare data (Headers + Rows)
        data = [df.columns.values.tolist()] + df.values.tolist()
        # 2. Wipe the old sheet so we don't have leftover data if we deleted rows
        _self.beveragetypes_sheet.clear()
        # 3. Write the new complete list
        _self.beveragetypes_sheet.update('A1', data)

    def update_sources_sheet(_self, df):
        # Overwrite the sources list
        data = [df.columns.values.tolist()] + df.values.tolist()
        _self.beveragesource_sheet.clear()
        _self.beveragesource_sheet.update('A1', data)
