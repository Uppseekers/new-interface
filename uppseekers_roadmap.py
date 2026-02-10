import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Admit AI | Snake Roadmap", layout="wide")

# --- CUSTOM STYLING (The "Secret Sauce") ---
st.markdown("""
<style>
    .roadmap-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        padding: 20px;
        background-color: #1a2a3a;
        border-radius: 15px;
    }
    .milestone-header {
        grid-column: span 3;
        background: linear-gradient(90deg, #e67e22, #d35400);
        color: white;
        padding: 15px;
        text-align: center;
        border-radius: 10px;
        font-weight: bold;
        font-size: 24px;
        margin: 20px 0;
    }
    .task-card {
        background-color: #2980b9;
        color: white;
        padding: 15px;
        border-radius: 12px;
        border-left: 8px solid #f1c40f;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.3);
        min-height: 100px;
    }
    .month-badge {
        background-color: #f1c40f;
        color: #1a2a3a;
        padding: 2px 8px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 12px;
        display: inline-block;
        margin-bottom: 8px;
    }
    .task-name {
        font-size: 14px;
        font-weight: 500;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

# --- APP UI ---
st.title("🐍 Admit AI: Complete Admissions Snake")

with st.sidebar:
    st.header("Settings")
    name = st.text_input("Student Name", "Aspirant")
    target_class = st.selectbox("Current Class", ["9th", "10th", "11th", "12th"])
    month_start = st.selectbox("Current Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])

# Load Excel Logic
excel_file = "Class wise Tentative Flow .xlsx"

if os.path.exists(excel_file):
    try:
        # Load data for the selected class
        df = pd.read_excel(excel_file, sheet_name=f"Class {target_class}")
        df.columns = df.columns.str.strip()

        # Filtering: Only show from the current month onwards
        if 'Month' in df.columns:
            mask = df['Month'].str.contains(month_start, case=False, na=False)
            if mask.any():
                df = df.iloc[df[mask].index[0]:].reset_index(drop=True)

        # --- BUILDING THE VISUAL SNAKE ---
        st.markdown('<div class="roadmap-container">', unsafe_allow_html=True)
        
        # Milestone Banner
        st.markdown(f'<div class="milestone-header">🚩 STARTING POINT: CLASS {target_class}</div>', unsafe_allow_html=True)

        for i, row in df.iterrows():
            month = str(row.get('Month', '')).upper()
            task = str(row.get('Task/Milestone', row.get('Task', 'Step')))
            
            # Logic for "Snake" direction (Visualizing connections)
            # Row 1: 1 -> 2 -> 3
            # Row 2: 6 <- 5 <- 4
            # This logic can be expanded, but for a "One Screen" view, 
            # a standard 3-column grid is much more readable.
            
            st.markdown(f"""
                <div class="task-card">
                    <div class="month-badge">{month}</div>
                    <div class="task-name">{task}</div>
                </div>
            """, unsafe_allow_html=True)

        # Final Milestone
        st.markdown(f'<div class="milestone-header">🎓 GOAL: UNIVERSITY ADMISSION</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading sheet: {e}")
else:
    st.error(f"Please upload '{excel_file}' to your GitHub repository.")
