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

st.container()
# Container 1: Filtered view of training data
with st.container():
    st.header("📊 Evaluation Overview by Batch & Training Program")

    # Sidebar-like filters
    col1, col2 = st.columns(2)
    with col1:
        selected_batch = st.selectbox("Select Batch", options=df["Batch"].dropna().unique(), index=0)
    with col2:
        selected_program = st.selectbox("Select Training Program", options=df["Program Pelatihan"].dropna().unique(), index=0)

    # Filter DataFrame based on selections
    filtered_df = df[(df["Batch"] == selected_batch) & (df["Program Pelatihan"] == selected_program)]

    # Display raw filtered table
    st.subheader("📄 Filtered Responses")
    st.dataframe(filtered_df, use_container_width=True)

    # Calculate mean per group of questions
    st.subheader("📈 Average Score per Question Group")

    average_scores = {
        "Training Material": filtered_df[columns_materi_pelatihan].mean().mean(),
        "Training Management": filtered_df[columns_materi_penyelenggaraan].mean().mean(),
        "Trainer Performance": filtered_df[columns_materi_tenaga_pelatih].mean().mean()
    }

    # Show as table
    st.write(pd.DataFrame(average_scores, index=["Average Score"]).T)

    # Plot comparison
    chart_data = pd.DataFrame({
        "Category": list(average_scores.keys()),
        "Average Score": list(average_scores.values())
    })

    fig = px.bar(chart_data, x="Category", y="Average Score", color="Category",
                 title="Average Score Comparison by Category",
                 text_auto=True, range_y=[0, 5])

    st.plotly_chart(fig, use_container_width=True)