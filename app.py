import streamlit as st
import pandas as pd
from data_loader import load_data

st.set_page_config(page_title="Dashboard Pengolahan Data Monev BPVP Bandung Barat", layout="wide")
st.subheader("All data from respondents")

# create refresh button for clear the cache
if st.button("Refresh Data"):
    st.cache_data.clear()

# call the data loader function
@st.cache_data
def get_data():
    return load_data()
# load data
df = get_data()
st.dataframe(df)

# contoh chart
if not df.empty and "Jenis Kelamin" in df.columns:
    st.subheader("Jumlah Respon per Jenis Kelamin")
    st.bar_chart(df["Jenis Kelamin"].value_counts())
