import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Admit AI | The Bridge Roadmap", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .roadmap-wrapper { background-color: #0f172a; padding: 40px; border-radius: 20px; }
    .milestone-banner {
        background: linear-gradient(90deg, #6366f1, #4338ca);
        color: white; padding: 20px; text-align: center; border-radius: 15px;
        font-size: 26px; font-weight: 800; margin: 30px 0;
    }
    .phase-divider {
        background: #ef4444; color: white; padding: 10px; text-align: center;
        border-radius: 8px; font-weight: bold; margin: 20px 0; text-transform: uppercase;
    }
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

# --- HELPER: MAP COUNTRY DETAILS ---
def get_country_details(row, country):
    if country == "USA":
        return row.get('USA (Private/Ivies)', 'Focus on Early Action / Regular Decision.')
    elif country == "UK":
        return row.get('UK (UCAS)', 'Follow UCAS deadlines.')
    elif country == "Singapore":
        return row.get('Singapore (NUS/NTU)', 'Academic excellence and local board prep.')
    elif country == "Germany":
        text = str(row.get('Singapore (NUS/NTU)', 'Research German Public Universities.'))
        return text.replace("Singapore", "Germany").replace("NUS/NTU", "Public Universities")
    elif country == "Australia":
        return row.get('Europe / Australia', 'Check GTE and entry requirements.')
    elif country == "Canada":
        text = str(row.get('Europe / Australia', 'Research SPP colleges and universities.'))
        return text.replace("Australia", "Canada")
    return ""

# --- APP UI ---
st.title("🐍 Admit AI: The Integrated Journey")

with st.sidebar:
    st.header("Step 1: Profile")
    name = st.text_input("Student Name", "Aspirant")
    target_class = st.selectbox("Current Class", ["9th", "10th", "11th", "12th"])
    target_country = st.selectbox("Target Country", ["USA", "UK", "Singapore", "Australia", "Canada", "Germany"])
    start_month = st.selectbox("Start Month", ["April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February", "March"])

excel_file = "Class wise Tentative Flow .xlsx"

if os.path.exists(excel_file):
    try:
        # --- 1. PREPARE CURRENT CLASS DATA ---
        df_current = pd.read_excel(excel_file, sheet_name=f"Class {target_class}")
        df_current.columns = [str(c).strip() for c in df_current.columns]
        
        # Filter from start month until July of "Last Year"
        if target_class != "12th":
            # Finding the start index
            start_mask = df_current['Month'].str.contains(start_month, case=False, na=False)
            start_idx = df_current[start_mask].index[0] if start_mask.any() else 0
            
            # User wants to follow until July. 
            # We look for the last row in this sheet that contains "July"
            july_mask = df_current['Month'].str.contains("July", case=False, na=False)
            end_idx = df_current[july_mask].index[-1] if july_mask.any() else len(df_current)-1
            
            roadmap_part1 = df_current.iloc[start_idx : end_idx + 1]
        else:
            # If student is already in 12th, part 1 is empty or we handle it differently
            roadmap_part1 = pd.DataFrame()

        # --- 2. PREPARE CLASS 12TH SPRINT DATA ---
        df_12 = pd.read_excel(excel_file, sheet_name="Class 12th")
        df_12.columns = [str(c).strip() for c in df_12.columns]
        
        # Start from August as requested
        aug_mask = df_12['Month'].str.contains("Aug", case=False, na=False)
        aug_idx = df_12[aug_mask].index[0] if aug_mask.any() else 1 # Default to row 1 (July-Aug)
        
        # Go until January journey as requested
        jan_mask = df_12['Month'].str.contains("Jan", case=False, na=False)
        end_12_idx = df_12[jan_mask].index[0] if jan_mask.any() else len(df_12)-1
        
        roadmap_part2 = df_12.iloc[aug_idx : end_12_idx + 1]

        # --- 3. RENDERING THE INTEGRATED SNAKE ---
        st.markdown('<div class="roadmap-wrapper">', unsafe_allow_html=True)
        st.markdown(f'<div class="milestone-banner">🎓 {name.upper()}\'S {target_country.upper()} JOURNEY</div>', unsafe_allow_html=True)

        # Part 1: Current Class (Foundation)
        if not roadmap_part1.empty:
            st.markdown(f'<div class="phase-divider">Phase 1: {target_class} Grade Foundation (Until July)</div>', unsafe_allow_html=True)
            for _, row in roadmap_part1.iterrows():
                st.markdown(f"""
                    <div class="task-card">
                        <div class="month-tag">{str(row.get('Month')).upper()}</div>
                        <div class="task-title">{row.get('Task Name', row.get('Phase', 'Milestone'))}</div>
                        <div class="task-details">{row.get('Outcome ', 'Building profile milestones.')}</div>
                    </div>
                    <div class="connector">↓</div>
                """, unsafe_allow_html=True)

        # Part 2: The 12th Grade Sprint (Switching sheets)
        st.markdown(f'<div class="phase-divider">Phase 2: Class 12th Final Admissions (Aug to Jan)</div>', unsafe_allow_html=True)
        for _, row in roadmap_part2.iterrows():
            details = get_country_details(row, target_country)
            st.markdown(f"""
                <div class="task-card">
                    <div class="month-tag">{str(row.get('Month')).upper()}</div>
                    <div class="task-title">{row.get('Phase', 'Admissions Step')}</div>
                    <div class="task-details">{details}</div>
                </div>
                <div class="connector">↓</div>
            """, unsafe_allow_html=True)

        st.markdown(f'<div class="milestone-banner">🎯 GOAL REACHED: {target_country.upper()} ADMISSION</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error building integrated roadmap: {e}")
else:
    st.error("Excel file not found.")
