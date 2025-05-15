import streamlit as st
import pandas as pd
from data_loader import load_data

st.set_page_config(page_title="Dashboard Pengolahan Data Monev BPVP Bandung Barat", layout="wide")
st.subheader("All data from respondents")

# Data Preperation
# call the data loader function
@st.cache_data
def get_data():
    return load_data()

# load data
df, columns_materi_pelatihan, columns_materi_penyelenggaraan, columns_materi_tenaga_pelatih = get_data()

# copy oringinal data to new dataframe
df_cleaned = df.copy()

# data cleaning > masking email address
def mask_email(email):
    if pd.isna(email) or not isinstance(email, str):
        return email
    username, _, domain = email.partition("@")
    masked_username = username[0] + "***" + username[-1] if len(username) > 2 else "***"
    masked_domain = domain[0] + "***" + domain[-1] if len(domain) > 2 else "***"
    return f"{masked_username}@{masked_domain}"

df_cleaned["Email Address"] = df_cleaned["Email Address"].apply(mask_email)

# data cleaning > drop unused columns
unused_columns = [
    "Tanggal Pelatihan (Awal)",
    "Tanggal Pelatihan (Akhir)",
]
df_cleaned.drop(unused_columns, axis=1, inplace=True)


# create refresh button for clear the cache
if st.button("Refresh Data"):
    st.cache_data.clear()

st.dataframe(df_cleaned)

ALL_PROGRAMS_OPTION = "Semua Program Pelatihan"

st.container()
# Container 1: Filtered view of training data
with st.container():
    st.header("📊 Evaluation Overview by Batch & Training Program")

    # Sidebar-like filters
    col1, col2 = st.columns(2)

    # Dropdown Batch
    with col1:
        selected_batch = st.selectbox(
            "Pilih Batch/Jenis Pelatihan", 
            options=sorted(df_cleaned["Batch"].dropna().unique()), 
            index=0
        )

    # Filter Program Pelatihan berdasarkan batch yang dipilih
    available_programs = df_cleaned[df_cleaned["Batch"] == selected_batch]["Program Pelatihan"].dropna().unique()
    available_programs = sorted(available_programs)
    available_programs.insert(0, ALL_PROGRAMS_OPTION)

    with col2:
        selected_program = st.selectbox(
            "Pilih Program Pelatihan", 
            options=available_programs
        )

    # Filter dataframe
    if selected_program == ALL_PROGRAMS_OPTION:
        filtered_df = df_cleaned[df_cleaned["Batch"] == selected_batch]
    else:
        filtered_df = df_cleaned[(df_cleaned["Batch"] == selected_batch) & (df_cleaned["Program Pelatihan"] == selected_program)]

    average_scores = {
        "Materi Pelatihan": filtered_df[columns_materi_pelatihan].mean().mean().round(2),
        "Penyelenggaraan/Manajemen": filtered_df[columns_materi_penyelenggaraan].mean().mean().round(2),
        "Tenaga Pelatih/Instruktur": filtered_df[columns_materi_tenaga_pelatih].mean().mean().round(2)
    }


    # Tampilkan dalam bentuk kartu
    st.markdown("### 📦 Rata-Rata per Kategori")

    # Bagi jadi 3 kolom untuk 3 kartu
    col1, col2, col3 = st.columns(3)

    # Template kartu
    def render_card(title, score, color="#f0f2f6"):
        st.markdown(f"""
            <div style="
                background-color:{color};
                padding:20px;
                border-radius:10px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                text-align:center;
            ">
                <h4 style="color:#333;">{title}</h4>
                <h1 style="color:#0072C6;">{score:.2f}</h1>
            </div>
        """, unsafe_allow_html=True)

    # Isi setiap kolom
    with col1:
        render_card("Materi Pelatihan", average_scores["Materi Pelatihan"])

    with col2:
        render_card("Penyelenggaraan/Manajemen", average_scores["Penyelenggaraan/Manajemen"])

    with col3:
        render_card("Tenaga Pelatih/Instruktur", average_scores["Tenaga Pelatih/Instruktur"])
    
    # Display raw filtered table
    st.subheader("📄 Filtered Responses")
    st.dataframe(filtered_df, use_container_width=True)