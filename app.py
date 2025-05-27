import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from io import BytesIO

st.set_page_config(page_title="Dashboard Pengolahan Data Monev BPVP Bandung Barat", layout="wide")
st.markdown("# Hasil Monitoring dan Evaluasi Pelatihan Berbasis Kompetensi (PBK) BPVP Bandung Barat")
st.divider()

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

# Define default program filter option
ALL_PROGRAMS_OPTION = "Semua Program Pelatihan"


# ----------------------------------------------- Container Here ------------------------------------------------------
# Filter section by batch and training program
with st.container():
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

    # Show total respondent and name of the instructor
    instructor_name_filtered_df = filtered_df["Nama tenaga pelatih/instruktur"].dropna().unique()
    instructor_name_filtered_df = ", ".join(instructor_name_filtered_df)
    st.markdown(f"**Jumlah responden:** {total_respondent_filtered_df}")
    st.markdown(f"**Nama Pengajar:** {instructor_name_filtered_df}")
    col1, col2, col3 = st.columns(3)
  
    # Show average scores as cards
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
       

    with col3:
        render_card("Tenaga Pelatih/Instruktur", average_scores["Tenaga Pelatih/Instruktur"])

    col1, col2, col3 = st.columns(3)

    with col2:
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

        st.markdown(f"""
        <div style='text-align: center;'>
            <h3>Total Rata-Rata Nilai: {total_avarage_scores_filtered_df}</h1>
            <div style='font-size: 30px; color: gold;'>{stars_display}</div>
            <p style='margin-top: 5px; font-size: 35px'>{rating_text}</p>
        </div>
        """, unsafe_allow_html=True)


    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### Jumlah peserta berdasarkan generasi")

        generation_order = ["Gen Z", "Milenial", "Gen X", "Boomer", "Silent Gen", "Unknown"]
        generation_counts = filtered_df["Generasi"].value_counts().reindex(generation_order).fillna(0).reset_index()
        generation_counts.columns = ["Generasi", "Jumlah"]

        fig = px.bar(
            generation_counts,
            x="Jumlah",
            y="Generasi",
            orientation="h",
            color="Generasi",  # Opsional: buat warnanya beda per generasi
            color_discrete_sequence=px.colors.qualitative.Set2,  # Atur warna
            text="Jumlah"  # Tampilkan jumlah di bar
        )

        fig.update_layout(
            xaxis_title="Jumlah Responden",
            yaxis_title="",
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=30, b=10)
        )

        fig.update_traces(textposition="outside")  # letakkan label di luar bar

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Distribusi Pendidikan")
        pendidikan_counts = filtered_df["Pendidikan terakhir anda"].value_counts()
        fig_pendidikan = px.pie(
            names=pendidikan_counts.index,
            values=pendidikan_counts.values,
            hole=0.5,  # Donut style
           
        )
        st.plotly_chart(fig_pendidikan, use_container_width=True)

    with col3:
        st.markdown("#### Distribusi Jenis Pekerjaan")
        pekerjaan_counts = filtered_df["Pekerjaan anda saat ini"].value_counts()
        fig_pekerjaan = px.pie(
            names=pekerjaan_counts.index,
            values=pekerjaan_counts.values,
            hole=0.5,  # Donut style
            
        )
        st.plotly_chart(fig_pekerjaan, use_container_width=True)

    def summarize_comments(comments, top_n=1):
        # Drop empty/null comments
        comments = [c for c in comments if isinstance(c, str) and c.strip()]
        if not comments:
            return ["No comments available."]
        
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(comments)
        
        # Hitung similarity antar komentar
        sim_matrix = cosine_similarity(tfidf_matrix)
        sim_scores = sim_matrix.sum(axis=1)
        
        # Ambil index komentar dengan nilai representasi tertinggi
        top_idx = sim_scores.argsort()[-top_n:][::-1]
        return [comments[i] for i in top_idx]

    # Contoh pemakaian untuk setiap kolom komentar pada materi pelatihan
    comment_columns = [col for col in filtered_df.columns if 'Komentar' in col]  # atau sebutkan langsung nama kolom

    st.markdown("## 💬 Ringkasan Komentar dari Peserta")
    st.markdown("Data komentar dibawah ini berdasarkan kemiripan kata dari tiap komentar, maka dipilih 1 komentar yang dapat mewakili (akurat 85%)")

    col1, col2, col3 = st.columns(3)
    columns = [col1, col2, col3]
    for i, col in enumerate(columns):
        if i < len(comment_columns):
            materi = comment_columns[i]
            comments = filtered_df[materi].dropna().tolist()
            summary = summarize_comments(comments)
            with col:
                st.markdown(f"**{materi}**")
                for s in summary:
                    st.info(f"💬 {s}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("Penilaian Kelebihan personal instruktur")
        st.info(summarize_comments(filtered_df["Penilaian Kelebihan dari Personal Instrukur"].dropna()))
    with col2:
        st.markdown("Penilaian Kekurangan personal instruktur")
        st.info(summarize_comments(filtered_df["Penilaian Kekurangan dari Personal Instrukur"].dropna()))  


    output = BytesIO()
    # Function for adding auto numbering
    def add_auto_number(df):
        df_with_number = df.copy()
        df_with_number.insert(0, 'No.', range(1, len(df_with_number) + 1))
        return df_with_number

    # Function to generate Excel file in memory
    def generate_excel(filtered_df, column_materi_pelatihan, column_materi_penyelenggaraan, column_materi_tenaga_pelatih):
        source_data = add_auto_number(filtered_df)

        materi_pelatihan = add_auto_number(filtered_df[["Email Address"] + column_materi_pelatihan])
        materi_penyelenggaraan = add_auto_number(filtered_df[["Email Address"] + column_materi_penyelenggaraan])
        materi_tenaga_pelatih = add_auto_number(filtered_df[["Email Address"] + column_materi_tenaga_pelatih])

        komentar_cols = [col for col in filtered_df.columns if "komentar" in col.lower() or "penilaian" in col.lower()]
        komentar = add_auto_number(filtered_df[["Email Address"] + komentar_cols])

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            source_data.to_excel(writer, sheet_name="source_data", index=False)
            materi_pelatihan.to_excel(writer, sheet_name="materi_pelatihan", index=False)
            materi_penyelenggaraan.to_excel(writer, sheet_name="materi_penyelenggaraan", index=False)
            materi_tenaga_pelatih.to_excel(writer, sheet_name="materi_tenaga_pelatih", index=False)
            komentar.to_excel(writer, sheet_name="komentar", index=False)

        output.seek(0)
        return output  # ← RETURN here is the key!

    output = generate_excel(
        filtered_df,
        columns_materi_pelatihan,
        columns_materi_penyelenggaraan,
        columns_materi_tenaga_pelatih
        )

    st.download_button(
        label="📥 Download Excel Data Monev",
        data=output,
        file_name="data_monev.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


 