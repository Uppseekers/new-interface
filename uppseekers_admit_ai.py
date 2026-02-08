import streamlit as st
import pandas as pd
import numpy as np

# --- 1. CONFIGURATION & LOGIC ---
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

# --- 2. DATA LOADING HELPER ---
def get_stream_files(selected_course):
    # Mapping based on your provided filenames
    mapping = {
        "CS/AI": ("set_cs-ai.csv", "benchmarking_cs.csv"),
        "Data Science and Statistics": ("set_ds-stats..csv", "benchmarking_ds.csv"),
        "Business and Administration": ("set_business.csv", "benchmarking_business.csv"),
        "Finance and Economics": ("set_finance&Eco..csv", "benchmarking_finance&economic.csv")
    }
    return mapping.get(selected_course)

# --- 3. UI - SIDEBAR ---
st.sidebar.header("Control Panel")
course = st.sidebar.selectbox("Select Student Stream", ["CS/AI", "Data Science and Statistics", "Business and Administration", "Finance and Economics"])
target_country = st.sidebar.selectbox("Target Country for Analysis", list(REGIONAL_WEIGHTS.keys()))

q_file, b_file = get_stream_files(course)

try:
    df_q = pd.read_csv(q_file)
    df_b = pd.read_csv(b_file)
except FileNotFoundError:
    st.error(f"Please ensure {q_file} and {b_file} are in the directory.")
    st.stop()

# --- 4. SCORING ENGINE ---
def calculate_weighted_score(category_points, country):
    weights = REGIONAL_WEIGHTS[country]
    total = 0
    # Map category scores to weights (matching order of CATEGORIES constant)
    for i, cat in enumerate(CATEGORIES):
        total += category_points.get(cat, 0) * weights[i]
    return round(total, 2)

# --- 5. MAIN INTERFACE ---
st.title(f"Profiling Tool: {course}")

col1, col2 = st.columns(2)

student_points = {}
tuned_points = {}

# We iterate through the questions in the file
questions = df_q['Specific Question'].unique()

with col1:
    st.subheader("📋 Student Current Selection")
    for i, q_text in enumerate(questions):
        row = df_q[df_q['Specific Question'] == q_text].iloc[0]
        cat = row['Category']
        
        # Create options list and score mapping
        options = {
            row['Option A (Elite / Product)']: row['Score A'],
            row['Option B (Strong / Product)']: row['Score B'],
            row['Option C (Baseline)']: row['Score C'],
            row['Option D (Beginner)']: row['Score D']
        }
        
        selection = st.selectbox(f"{cat}: {q_text}", list(options.keys()), key=f"std_{i}")
        student_points[cat] = student_points.get(cat, 0) + options[selection]

with col2:
    st.subheader("🔧 Counselor Tuning (Desired)")
    for i, q_text in enumerate(questions):
        row = df_q[df_q['Specific Question'] == q_text].iloc[0]
        cat = row['Category']
        options = {
            row['Option A (Elite / Product)']: row['Score A'],
            row['Option B (Strong / Product)']: row['Score B'],
            row['Option C (Baseline)']: row['Score C'],
            row['Option D (Beginner)']: row['Score D']
        }
        
        # Default to what the student picked
        std_idx = list(options.keys()).index(st.session_state[f"std_{i}"])
        tuned_selection = st.selectbox(f"Tune {cat}: {q_text}", list(options.keys()), index=std_idx, key=f"tune_{i}")
        tuned_points[cat] = tuned_points.get(cat, 0) + options[tuned_selection]

# --- 6. RESULTS & BENCHMARKING ---
st.divider()

curr_score = calculate_weighted_score(student_points, target_country)
desired_score = calculate_weighted_score(tuned_points, target_country)

# Display Scores Side-by-Side
m1, m2 = st.columns(2)
m1.metric("Current Profiling Score", curr_score)
m2.metric("Desired (Tuned) Score", desired_score, delta=round(desired_score - curr_score, 2))

if st.button("Generate University Benchmark Report"):
    st.header(f"University Recommendations: {target_country}")
    
    # Filter universities for the selected country
    country_df = df_b[df_b['Country'] == target_country].copy()
    
    def get_status(score, benchmark):
        if score >= benchmark:
            return "✅ Safe to Target"
        elif score >= (benchmark * 0.85):
            return "⚠️ Need Strengthening"
        else:
            return "🚨 Significant Gap"

    country_df['Current Status'] = country_df['Total Benchmark Score'].apply(lambda x: get_status(curr_score, x))
    country_df['Desired Status'] = country_df['Total Benchmark Score'].apply(lambda x: get_status(desired_score, x))
    
    # Display the final table
    st.dataframe(
        country_df[['University', 'Total Benchmark Score', 'Current Status', 'Desired Status']],
        use_container_width=True
    )
