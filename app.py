import streamlit as st
import pandas as pd
from data_loader import load_data

st.set_page_config(page_title="Dashboard dari Google Form", layout="wide")
st.title("📊 Dashboard Data Google Form (Cols A–CG)")

# load data
df = load_data()
st.dataframe(df)

# contoh chart
if not df.empty and "Jenis Kelamin" in df.columns:
    st.subheader("Jumlah Respon per Jenis Kelamin")
    st.bar_chart(df["Jenis Kelamin"].value_counts())
