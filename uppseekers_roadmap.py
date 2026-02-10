import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Admit AI | Transition Roadmap", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .roadmap-wrapper { background-color: #0f172a; padding: 40px; border-radius: 20px; }
    .milestone-banner {
        background: linear-gradient(90deg, #6366f1, #4338ca);
        color: white; padding: 20px; text-align: center; border-radius: 15px;
        font-size: 26px; font-weight: 800; margin: 30px 0;
    }
    .phase-label { color: #fbbf24; font-size: 14px; font-weight: bold; margin-bottom: 5px; }
    .task-card {
        background: #1e293b; border-left: 6px solid #fbbf24;
        padding: 25px; border-radius: 12px; margin-bottom: 10px;
    }
    .month-tag {
        background: #fbbf24; color: #1e293b; font-weight: 800;
        padding: 4px 12px; border-radius: 6px; font-size: 13px; margin-bottom: 10px; display: inline-block;
    }
    .task-title { color: #f8fafc; font-size: 20px; font-weight: 700; margin-bottom: 8px; }
    .task-details { color: #cbd5e1; font-size: 15px; line-height: 1.6; }
    .connector { text-align: center; color: #334155; font-size: 30px; margin: -5px 0; }
</style>
""", unsafe_allow_html=True)

# Helper to process Class 12 logic for specific countries
def get_country_details(row, country):
    if country == "USA":
        return row.get('USA (Private/Ivies)', 'Apply/Research Universities.')
    elif country == "UK":
        return row.get('UK (UCAS)', 'Follow UCAS process.')
    elif country == "Singapore":
        return row.get('Singapore (NUS/NTU)', 'Academic review.')
    elif country == "Germany":
        raw = str(row.get('Singapore (NUS/NTU)', 'Public University prep.'))
        return raw.replace("Singapore", "Germany").replace("NUS/NTU", "Public Universities")
    elif country == "Australia":
        return row.get('Europe / Australia', 'Visa and Entry prep.')
    elif country == "Canada":
        raw = str(row.get('Europe / Australia', 'Application prep.'))
        return raw.replace("Australia", "Canada")
    return "Global application prep."

# --- APP UI ---
st.title("🐍 The Admissions Bridge: Journey to University")

with st.sidebar:
    st.header("Profile Configuration")
    name = st.text_input("Student Name", "Aspirant")
    current_class = st.selectbox("Current Class", ["9th", "10th", "11th", "12th"])
    target_country = st.selectbox("Target Country", ["USA", "UK", "Singapore", "Australia", "Canada", "Germany"])
    start_month = st.selectbox("Start Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])

excel_file = "Class wise Tentative Flow .xlsx"

if os.path.exists(excel_file):
    try:
        # 1. LOAD DATA
        df_current = pd.read_excel(excel_file, sheet_name=f"Class {current_class}")
        df_current.columns = [str(c).strip() for c in df_current.columns]
        
        df_12 = pd.read_excel(excel_file, sheet_name="Class 12th")
        df_12.columns = [str(c).strip() for c in df_12.columns]

        # 2. SEPARATE JOURNEYS
        # We define August as the transition point
        months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        aug_idx = months_order.index("August")
        start_idx = months_order.index(start_month)

        combined_data = []

        # Part A: Current Class Plan (From Start Month until July)
        # If user starts after July, we skip this and jump straight to Class 12
        if start_idx < aug_idx and current_class != "12th":
            # Filter current grade's sheet for months before August
            pre_aug_df = df_current[~df_current['Month'].str.contains('August|September|October|November|December', case=False, na=False)]
            # Further filter by selected start month
            mask = pre_aug_df['Month'].str.contains(start_month, case=False, na=False)
            if mask.any():
                pre_aug_df = pre_aug_df.iloc[pre_aug_df[mask].index[0]:]
            
            for _, row in pre_aug_df.iterrows():
                combined_data.append({
                    "Month": row.get('Month'),
                    "Title": row.get('Task Name', row.get('Phase', 'Requirement')),
                    "Details": row.get('Outcome ', 'Academic and profile building.'),
                    "Phase": "Current Grade Preparation"
                })

        # Part B: Class 12th Plan (From August to January)
        # We always include Class 12th Aug-Jan journey as the "Final Stretch"
        post_aug_df = df_12[df_12['Month'].str.contains('August|September|October|November|December|January', case=False, na=False)]
        
        # If current class is already 12th, filter by start month
        if current_class == "12th":
            mask = post_aug_df['Month'].str.contains(start_month, case=False, na=False)
            if mask.any():
                post_aug_df = post_aug_df.iloc[post_aug_df[mask].index[0]:]

        for _, row in post_aug_df.iterrows():
            combined_data.append({
                "Month": row.get('Month'),
                "Title": row.get('Phase', 'Admissions Step'),
                "Details": get_country_details(row, target_country),
                "Phase": f"Class 12th {target_country} Journey"
            })

        # --- RENDER ROADMAP ---
        st.markdown('<div class="roadmap-wrapper">', unsafe_allow_html=True)
        st.markdown(f'<div class="milestone-banner">🚩 {name.upper()}\'S ADMISSIONS ROADMAP</div>', unsafe_allow_html=True)

        for i, item in enumerate(combined_data):
            # Render Card
            st.markdown(f"""
                <div class="phase-label">{item['Phase']}</div>
                <div class="task-card">
                    <div class="month-tag">{str(item['Month']).upper()}</div>
                    <div class="task-title">{item['Title']}</div>
                    <div class="task-details">{item['Details']}</div>
                </div>
                <div class="connector">↓</div>
            """, unsafe_allow_html=True)

        st.markdown(f'<div class="milestone-banner">🎓 ADMISSION SECURED IN {target_country.upper()}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error building roadmap: {e}")
else:
    st.error("Excel file not found.")
