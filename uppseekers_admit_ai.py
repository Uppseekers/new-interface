import streamlit as st
import pandas as pd
import numpy as np

# --- 1. DATA CONFIGURATION ---
REGIONAL_WEIGHTS = {
    "USA": [0.20, 0.10, 0.05, 0.05, 0.15, 0.05, 0.20, 0.10, 0.05, 0.05],
    "UK": [0.25, 0.10, 0.05, 0.05, 0.30, 0.02, 0.10, 0.03, 0.00, 0.10],
    "Germany": [0.35, 0.10, 0.05, 0.05, 0.05, 0.00, 0.35, 0.00, 0.00, 0.05],
    "Singapore": [0.30, 0.10, 0.10, 0.15, 0.10, 0.02, 0.15, 0.03, 0.00, 0.05],
    "Australia": [0.30, 0.10, 0.10, 0.05, 0.10, 0.05, 0.20, 0.05, 0.00, 0.05],
    "Canada": [0.25, 0.10, 0.05, 0.05, 0.15, 0.05, 0.20, 0.10, 0.00, 0.05],
    "Netherlands": [0.35, 0.15, 0.05, 0.05, 0.10, 0.00, 0.25, 0.00, 0.00, 0.05],
    "European Countries": [0.30, 0.15, 0.05, 0.05, 0.10, 0.05, 0.20, 0.05, 0.00, 0.05],
    "Japan": [0.40, 0.10, 0.10, 0.10, 0.10, 0.00, 0.10, 0.05, 0.00, 0.05],
    "Other Asian": [0.40, 0.10, 0.15, 0.10, 0.05, 0.02, 0.10, 0.03, 0.00, 0.05]
}

CATEGORIES = ["Academics", "Rigor", "Testing", "Merit", "Research", "Engagement", "Experience", "Impact", "Public Voice", "Recognition"]

st.set_page_config(layout="wide", page_title="University Readiness Profiler")

# --- 2. INDEX LOOKUP LOGIC ---
@st.cache_data
def load_file_indices():
    # Load Sheet1 from both main workbooks to act as the index
    try:
        # Assuming the main uploaded files are named exactly this or similar
        questions_index = pd.read_excel("University Readiness_new (3) (1).xlsx", sheet_name="Sheet1")
        benchmarking_index = pd.read_excel("Benchmarking_USA (3) (2) (1).xlsx", sheet_name="Sheet1")
        return questions_index, benchmarking_index
    except Exception as e:
        st.error(f"Error loading index sheets: {e}")
        return None, None

q_index, b_index = load_file_indices()

# --- 3. UI - SIDEBAR ---
st.sidebar.header("Control Panel")
if q_index is not None:
    # Dynamically pull available streams from the index sheet
    streams = q_index['Stream'].unique().tolist()
    selected_stream = st.sidebar.selectbox("Select Student Stream", streams)
    target_country = st.sidebar.selectbox("Target Country", list(REGIONAL_WEIGHTS.keys()))

    # Find relevant data sheets based on index lookup
    # Adjust column names 'Stream' and 'File_Name' to match your Sheet1 structure
    q_file_name = q_index[q_index['Stream'] == selected_stream]['File_Name'].values[0]
    b_file_name = b_index[b_index['Stream'] == selected_stream]['File_Name'].values[0]
    
    # Load the specific question/benchmarking data
    df_q = pd.read_csv(q_file_name)
    df_b = pd.read_csv(b_file_name)
else:
    st.stop()

# --- 4. SCORING ENGINE ---
def calculate_score(points_dict, country):
    weights = REGIONAL_WEIGHTS[country]
    total = sum(points_dict.get(cat, 0) * weights[i] for i, cat in enumerate(CATEGORIES))
    return round(total, 2)

# --- 5. INTERACTIVE PROFILING ---
st.title(f"Profiling Dashboard: {selected_stream}")

col1, col2 = st.columns(2)
student_points = {}
tuned_points = {}

questions = df_q['Specific Question'].unique()

with col1:
    st.subheader("Student Selection")
    for i, q_text in enumerate(questions):
        row = df_q[df_q['Specific Question'] == q_text].iloc[0]
        cat = row['Category']
        opts = {row[f'Option {x}']: row[f'Score {x}'] for x in ['A', 'B', 'C', 'D']}
        
        choice = st.selectbox(f"{cat}: {q_text}", list(opts.keys()), key=f"s_{i}")
        student_points[cat] = student_points.get(cat, 0) + opts[choice]

with col2:
    st.subheader("Counselor Tuning")
    for i, q_text in enumerate(questions):
        row = df_q[df_q['Specific Question'] == q_text].iloc[0]
        cat = row['Category']
        opts = {row[f'Option {x}']: row[f'Score {x}'] for x in ['A', 'B', 'C', 'D']}
        
        # Sync tuning with student choice by default
        std_val = st.session_state[f"s_{i}"]
        tune_choice = st.selectbox(f"Adjust: {q_text}", list(opts.keys()), 
                                    index=list(opts.keys()).index(std_val), key=f"t_{i}")
        tuned_points[cat] = tuned_points.get(cat, 0) + opts[tune_choice]

# --- 6. OUTPUT & REPORTING ---
st.divider()
curr_score = calculate_score(student_points, target_country)
tune_score = calculate_score(tuned_points, target_country)

m1, m2 = st.columns(2)
m1.metric("Current Score", curr_score)
m2.metric("Tuned Score", tune_score, delta=round(tune_score - curr_score, 2))

if st.button("Generate Benchmark Report"):
    country_df = df_b[df_b['Country'] == target_country].copy()
    
    def get_tier(score, bench):
        if score >= bench: return "✅ Safe to Target"
        if score >= (bench * 0.9): return "⚠️ Need Strengthening"
        return "🚨 Significant Gap"

    country_df['Current'] = country_df['Total Benchmark Score'].apply(lambda x: get_tier(curr_score, x))
    country_df['Tuned'] = country_df['Total Benchmark Score'].apply(lambda x: get_tier(tune_score, x))
    
    st.table(country_df[['University', 'Total Benchmark Score', 'Current', 'Tuned']])
