import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="University Profiling Tool")

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

# --- HELPER FUNCTIONS ---
def calculate_regional_score(category_scores, weights):
    # category_scores: list of 10 values
    return sum(s * w for s, w in zip(category_scores, weights))

def get_status(score, benchmark):
    if score >= benchmark:
        return "✅ Safe to Target"
    elif score >= (benchmark * 0.85):
        return "⚠️ Need Strengthening"
    else:
        return "❌ Significant Gap"

# --- SIDEBAR: FILE UPLOADS ---
st.sidebar.header("Upload Files")
q_file = st.sidebar.file_uploader("Upload Readiness File (Questions)", type=['xlsx'])
b_file = st.sidebar.file_uploader("Upload Benchmarking File", type=['xlsx'])

if q_file and b_file:
    df_q = pd.read_excel(q_file)
    df_b = pd.read_excel(b_file)

    # Stream Selection
    streams = df_q['Stream'].unique()
    selected_stream = st.sidebar.selectbox("Select Student Stream", streams)
    filtered_q = df_q[df_q['Stream'] == selected_stream]

    st.title(f"Profiling: {selected_stream}")

    # Layout for Side-by-Side Questioning
    col_student, col_counselor = st.columns(2)
    
    student_selections = {}
    tuned_selections = {}

    with col_student:
        st.header("Student Current Profile")
        for cat in CATEGORIES:
            st.subheader(f"Category: {cat}")
            cat_qs = filtered_q[filtered_q['Category'] == cat]
            for i, row in cat_qs.iterrows():
                # Assuming options are stored in a way we can extract
                options = [row['Option 1'], row['Option 2'], row['Option 3']] # Adjust based on your Excel headers
                student_selections[row['Question']] = st.selectbox(f"{row['Question']}", options, key=f"std_{i}")

    with col_counselor:
        st.header("Counselor Tuning (Target)")
        for cat in CATEGORIES:
            st.subheader(f"Tuning: {cat}")
            cat_qs = filtered_q[filtered_q['Category'] == cat]
            for i, row in cat_qs.iterrows():
                options = [row['Option 1'], row['Option 2'], row['Option 3']]
                tuned_selections[row['Question']] = st.selectbox(f"Desired: {row['Question']}", options, key=f"cns_{i}")

    # --- SCORE CALCULATION ---
    # Map selections to scores based on the Excel 'Marking' logic
    def get_total_cat_score(selections_dict):
        cat_totals = []
        for cat in CATEGORIES:
            score = 0
            # Logic to sum marks for each category from df_q
            cat_totals.append(score) # Placeholder for logic mapping options to marks
        return cat_totals

    # Example Results Display
    st.divider()
    target_country = st.selectbox("Select Country for Benchmarking", list(REGIONAL_WEIGHTS.keys()))
    
    # Final Benchmarking Table
    st.header(f"University Benchmarking Report - {target_country}")
    # (Here you would merge the scores with df_b)
    st.dataframe(df_b[df_b['Country'] == target_country])

else:
    st.warning("Please upload both Excel files to begin.")
