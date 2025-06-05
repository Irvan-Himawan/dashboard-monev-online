import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

load_dotenv()
gsheet_id = os.getenv("gsheet_id")
gspread_json_path = os.getenv("GSPREAD_JSON")

if not gsheet_id:
    raise ValueError("gsheet_id is not set in the .env file.")
if not gspread_json_path:
    raise ValueError("GSPREAD_JSON is not set in the .env file.")
if not os.path.exists(gspread_json_path):
    raise FileNotFoundError(f"GSPREAD_JSON path not found: {gspread_json_path}")

with open(gspread_json_path) as f:
    creds_dict = json.load(f)

def get_credentials():
    return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
