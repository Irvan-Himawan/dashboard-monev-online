import pandas as pd
import gspread
from config import get_credentials, gsheet_id

def load_data():
    creds = get_credentials()
    client = gspread.authorize(creds)

    # --- ambil hanya range A:CG ---
    sh = client.open_by_key(gsheet_id)
    sheet = sh.worksheet("Form Responses 1")
    # Method 1: pakai get() dengan A1 notation
    raw = sheet.get("A:CF")
    # Alternatif Method 2: ambil semua lalu slice 85 kolom pertama
    # raw_full = sheet.get_all_values()
    # raw = [row[:85] for row in raw_full]

    # --- proses header & rows ---
    header = raw[0]
    data_rows = [r for r in raw[1:] if r != header]

    df = pd.DataFrame(data_rows, columns=header)
    return df