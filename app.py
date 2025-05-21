import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data

st.set_page_config(page_title="Dashboard Pengolahan Data Monev BPVP Bandung Barat", layout="wide")
st.subheader("All data from respondents")

# Load and cache the data
@st.cache_data
def get_data():
    return load_data()

df, columns_materi_pelatihan, columns_materi_penyelenggaraan, columns_materi_tenaga_pelatih = get_data()

# Make a clean copy of the original dataframe
df_cleaned = df.copy()

# Normalize Column
## Edit column Email Address - Mask email addresses for privacy
def mask_email(email):
    if pd.isna(email) or not isinstance(email, str):
        return email
    username, _, domain = email.partition("@")
    masked_username = username[0] + "***" + username[-1] if len(username) > 2 else "***"
    masked_domain = domain[0] + "***" + domain[-1] if len(domain) > 2 else "***"
    return f"{masked_username}@{masked_domain}"

df_cleaned["Email Address"] = df_cleaned["Email Address"].apply(mask_email)

## Create column generasi - classification age by generazation
def classify_generation(age):
        try:
            age = int(age)
        except:
            return "Unknown"

        if age <= 0:
            return "Unknown"
        elif age <= 26:
            return "Gen Z"
        elif age <= 42:
            return "Milenial"
        elif age <= 58:
            return "Gen X"
        elif age <= 76:
            return "Boomer"
        else:
            return "Silent Gen"
df_cleaned["Generasi"] = df_cleaned["Usia anda saat ini?"].apply(classify_generation)

## Drop unnecessary columns
unused_columns = [
    "Tanggal Pelatihan (Awal)",
    "Tanggal Pelatihan (Akhir)",
]
df_cleaned.drop(unused_columns, axis=1, inplace=True)


# ----------------------------------------------- Dashboard Start Here ------------------------------------------------------
# Refresh button to clear cache
if st.button("Refresh Data"):
    st.cache_data.clear()

# Display raw data
st.dataframe(df_cleaned)

# Define default program filter option
ALL_PROGRAMS_OPTION = "Semua Program Pelatihan"

# Filter section by batch and training program
with st.container():
    st.header("📊 Evaluation Overview by Batch & Training Program")

    col1, col2 = st.columns(2)

    # Batch selection
    with col1:
        selected_batch = st.selectbox(
            "Pilih Batch/Jenis Pelatihan",
            options=sorted(df_cleaned["Batch"].dropna().unique()),
            index=0
        )

    # Filter available programs based on selected batch
    available_programs = df_cleaned[df_cleaned["Batch"] == selected_batch]["Program Pelatihan"].dropna().unique()
    available_programs = sorted(available_programs)
    available_programs.insert(0, ALL_PROGRAMS_OPTION)

    with col2:
        selected_program = st.selectbox(
            "Pilih Program Pelatihan",
            options=available_programs
        )

    # Filter the dataframe accordingly
    if selected_program == ALL_PROGRAMS_OPTION:
        filtered_df = df_cleaned[df_cleaned["Batch"] == selected_batch]
    else:
        filtered_df = df_cleaned[(df_cleaned["Batch"] == selected_batch) & (df_cleaned["Program Pelatihan"] == selected_program)]

    # Calculate average scores by group
    average_scores = {
        "Materi Pelatihan": filtered_df[columns_materi_pelatihan].mean().mean().round(2),
        "Penyelenggaraan/Manajemen": filtered_df[columns_materi_penyelenggaraan].mean().mean().round(2),
        "Tenaga Pelatih/Instruktur": filtered_df[columns_materi_tenaga_pelatih].mean().mean().round(2)
    }
    # Count responded per filter
    total_respondent_filtered_df = filtered_df.shape[0]

    # Avarage scores per filter
    total_avarage_scores_filtered_df = filtered_df[columns_materi_tenaga_pelatih + columns_materi_penyelenggaraan + columns_materi_pelatihan].mean().mean().round(2)

    # Show average scores as cards
    st.markdown(f"**Jumlah responden :** {total_respondent_filtered_df}")
    col1, col2, col3 = st.columns(3)

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

    with col1:
        render_card("Materi Pelatihan", average_scores["Materi Pelatihan"])

    with col2:
        render_card("Penyelenggaraan/Manajemen", average_scores["Penyelenggaraan/Manajemen"])
        # create rating for average scores (all materi)
        # Define rating logic
        def get_rating_and_stars(score):
            if score == 5:
                return "Sangat Puas", 5
            elif score >= 4:
                return "Puas", 4
            elif score >= 3:
                return "Cukup Puas", 3
            elif score >= 2:
                return "Kurang Puas", 2
            else:
                return "Sangat Tidak Puas", 1

        rating_text, star_count = get_rating_and_stars(total_avarage_scores_filtered_df)
        stars_display = "⭐" * star_count

        st.header("**Rata-rata Nilai**")
        st.subheader(total_avarage_scores_filtered_df)
        st.subheader(stars_display)

    with col3:
        render_card("Tenaga Pelatih/Instruktur", average_scores["Tenaga Pelatih/Instruktur"])

    # Display filtered raw data table
    st.subheader("📄 Filtered Responses")
    st.dataframe(filtered_df, use_container_width=True)

     
    # Show bar chart of generation distribution
    st.subheader("\U0001F465 Respondent Distribution by Generation")
    generation_order = ["Gen Z", "Milenial", "Gen X", "Boomer", "Silent Gen", "Unknown"]
    generation_counts = df_cleaned["Generasi"].value_counts().reindex(generation_order).fillna(0)
    st.bar_chart(generation_counts, horizontal=True)
