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

    # cleaning dataset

    # Grouping questions columns
    columns_materi_pelatihan = [
    "1. Tulisan di dalam materi pelatihan jelas dan mudah di baca",
    "2. Kualitas materi pelatihan dapat menambah tingkat keterampilan dan pengetahuan anda",
    "3. Materi pelatihan mudah di pahami dan mudah diterapkan dalam praktek",
    "4. Materi pelatihan telah sesuai dengan harapan anda"
    ]

    columns_materi_penyelenggaraan =  [
        "1. Pelayanan administrasi pelatihan diberikan dengan baik, cepat tanggap dan jelas",
        "2. Pelaksanaan pelatihan dimonitor dengan baik",
        "3. Keluhan peserta pelatihan direspon dengan cepat dan positif",
        "4. Platform pelatihan yang mudah diakses",
        "5. Pembelajaran online selama pelatihan dianggan berkualitas baik"
    ]

    columns_materi_tenaga_pelatih = [
        "1. Menguasai materi pelatihan teori dan praktek",
        "2. Menyajikan pelajaran dengan jelas dan bahasanya mudah dimengerti",
        "3. Memberikan materi sesuai dengan tujuan pembelajaran secara sistematis/berurutan",
        "4. Memberikan kesempatan pada peserta pelatihan untuk bertanya atau menyampaikan pendapat",
        "5. Menciptakan suasana belajar yang  kondusif (aman dan nyaman)",
        "6. Hadir tepat waktu sesuai jadwal"
    ]

    combine_questions_columns = (
        columns_materi_pelatihan +
        columns_materi_penyelenggaraan +
        columns_materi_tenaga_pelatih
    )

    # Filtering data by unique email and program name based on the latest timestamp
    df = df[df['Email Address'].notna() & (df['Email Address'] != ' ')]
    df = df.sort_values(by=['Nama Program pelatihan yang anda ikuti','Timestamp'],ascending=False)
    df = df.reset_index(drop=True)
    df = df.drop_duplicates(subset=['Email Address','Nama Program pelatihan yang anda ikuti'], keep='first')

    # convert questions columns to numeric
    df[combine_questions_columns] = df[combine_questions_columns].apply(pd.to_numeric, errors='coerce').astype('Int64')

    # split in column nama program pelatihan into 2 columns (batch and program name)
    df[['Batch', 'Program Pelatihan']] = df['Nama Program pelatihan yang anda ikuti'].str.extract(r'(Batch \d+)\s*-\s*(.+)', expand=True)
    df['Batch'] = df['Batch'].str.strip()
    df['Program Pelatihan'] = df['Program Pelatihan'].str.strip()
    return df