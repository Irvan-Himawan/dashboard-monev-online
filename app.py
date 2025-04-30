import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import get_credentials, gsheet_id

st.set_page_config(page_title="Dashboard dari Google Form", layout="wide")
st.title("📊 Dashboard Data Google Form (Cols A–CG)")

@st.cache_data
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
    # buat header unik jika perlu
    def make_unique(headers):
        seen = {}
        out = []
        for h in headers:
            if not h:
                h = "Unnamed"
            if h in seen:
                seen[h] += 1
                out.append(f"{h}_{seen[h]}")
            else:
                seen[h] = 0
                out.append(h)
        return out

    uniq_header = make_unique(header)
    # buang baris yang sama persis dengan header (jika impor ulang menyertakan header lagi)
    data_rows = [r for r in raw[1:] if r != header]

    df = pd.DataFrame(data_rows, columns=uniq_header)
    return df

df = load_data()
st.dataframe(df)

# contoh chart
if not df.empty and "Jenis Kelamin" in df.columns:
    st.subheader("Jumlah Respon per Jenis Kelamin")
    st.bar_chart(df["Jenis Kelamin"].value_counts())
