import os
import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

# Scope untuk akses Google Sheets & Drive
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

# Deteksi apakah dijalankan di Streamlit Cloud atau lokal
if "gsheets" in st.secrets:
    # ✅ Jika di Streamlit Cloud
    creds_dict = st.secrets["gsheets"]
    gsheet_id = st.secrets["general"]["gsheet_id"]
else:
    # ✅ Jika dijalankan secara lokal
    from dotenv import load_dotenv
    load_dotenv()

    gsheet_id = os.getenv("gsheet_id")
    json_path = os.getenv("GSPREAD_JSON")

    if not gsheet_id:
        raise ValueError("gsheet_id not found in .env")

    if not json_path or not os.path.exists(json_path):
        raise FileNotFoundError(f"GSPREAD_JSON not found or path is invalid: {json_path}")

    with open(json_path, "r") as f:
        creds_dict = json.load(f)

# Fungsi untuk mengembalikan credentials
def get_credentials():
    return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
