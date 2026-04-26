import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- GOOGLE SHEETS SETUP ---
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Liquid Tracker").sheet1 

# --- APP UI ---
st.set_page_config(page_title="Liquid Tracker", page_icon="💧")

st.title("💧 Liquid Tracker")

# 1. Quick Stats (Dashboard)
data = sheet.get_all_records()
if data:
    # Basic math for today's total (assuming you have 'Date' and 'Amount' columns)
    today = datetime.now().strftime("%Y-%m-%d")
    today_total = sum(int(row['Amount']) for row in data if str(row['Date']) == today)
    
    col1, col2 = st.columns(2)
    col1.metric("Today's Intake", f"{today_total} ml")
    col2.metric("Goal", "2000 ml", delta=f"{today_total - 2000} ml")

st.divider()

# 2. Input Form (Write Data)
st.subheader("Log New Drink")
with st.form("log_form", clear_on_submit=True):
    liquid_type = st.selectbox("What did you drink?", ["Water", "Coffee", "Tea", "Juice", "Soda"])
    amount = st.number_input("Amount (ml)", min_value=0, step=50, value=250)
    note = st.text_input("Note (Optional)")
    
    submit = st.form_submit_button("Log Entry", use_container_width=True)

    if submit:
        # Prepare the row data
        new_row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), liquid_type, amount, note]
        sheet.append_row(new_row)
        st.success(f"Logged {amount}ml of {liquid_type}!")
        st.rerun() # Refresh the page to update stats

# 3. Recent History (Read Data)
st.divider()
st.subheader("Recent Logs")
if data:
    # Show last 5 entries, reversed so newest is on top
    st.table(data[-5:][::-1])
else:
    st.info("No logs found yet. Start drinking!")