# Existing imports
import streamlit as st
import qrcode
import io
import uuid
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("your-service-account.json", scope)  # replace with your actual file
client = gspread.authorize(creds)
sheet = client.open("AttendanceLog").sheet1  # make sure this Sheet exists

# Token store (in-memory)
TOKEN_EXPIRY_SECONDS = 60
tokens = {}

def generate_token():
    token = str(uuid.uuid4())
    tokens[token] = datetime.now() + timedelta(seconds=TOKEN_EXPIRY_SECONDS)
    return token

def is_token_valid(token):
    return token in tokens and datetime.now() <= tokens[token]

def generate_qr_url(base_url, token):
    params = {'token': token}
    return f"{base_url}?{urlencode(params)}"

def generate_qr_image(url):
    qr = qrcode.make(url)
    buf = io.BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

# Streamlit layout
st.set_page_config(page_title="QR Attendance", layout="centered")
st.title("📸 QR Code Attendance System")

# QR Code view
st.subheader("Scan this QR to mark attendance")
base_url = "https://YOUR-STREAMLIT-APP-URL.streamlit.app"  # Replace with your deployed app URL
token = generate_token()
qr_url = generate_qr_url(base_url, token)
img = generate_qr_image(qr_url)
st.image(img)

# Attendance form
query_params = st.query_params
if 'token' in query_params:
    user_token = query_params['token'][0]
    if is_token_valid(user_token):
        with st.form("attendance_form"):
            name = st.text_input("Enter your name")
            submit = st.form_submit_button("Submit")
            if submit:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sheet.append_row([name, timestamp])
                st.success(f"✅ Attendance marked for {name} at {timestamp}")
    else:
        st.error("❌ Invalid or expired token.")
