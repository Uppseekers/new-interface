import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Admit AI | Country Specific Roadmap", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .roadmap-wrapper { background-color: #0f172a; padding: 40px; border-radius: 20px; }
    .milestone-banner {
        background: linear-gradient(90deg, #6366f1, #4338ca);
        color: white; padding: 20px; text-align: center; border-radius: 15px;
        font-size: 26px; font-weight: 800; margin: 30px 0;
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

# --- APP UI ---
st.title("🐍 Personalized Admissions Snake")

with st.sidebar:
    st.header("Step 1: Student Profile")
    name = st.text_input("Name", "Aspirant")
    target_class = st.selectbox("Current Class", ["9th", "10th", "11th", "12th"])
    
    # NEW: Country Selection
    target_country = st.selectbox("Target Country", 
        ["USA", "UK", "Singapore", "Australia", "Canada", "Germany"])
    
    start_month = st.selectbox("Current Month", [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ])

excel_file = "Class wise Tentative Flow .xlsx"

if os.path.exists(excel_file):
    try:
        # 1. Load Data
        df = pd.read_excel(excel_file, sheet_name=f"Class {target_class}")
        # Clean column names (remove leading/trailing spaces)
        df.columns = [str(c).strip() for c in df.columns]

        # 2. Filter by Month
        if 'Month' in df.columns:
            mask = df['Month'].str.contains(start_month, case=False, na=False)
            if mask.any():
                df = df.iloc[df[mask].index[0]:].reset_index(drop=True)

        # 3. Country Mapping Logic (Specifically for Class 12)
        # Class 12 Columns: Month, Phase, USA (Private/Ivies), UK (UCAS), Singapore (NUS/NTU), Europe / Australia
        
        st.markdown('<div class="roadmap-wrapper">', unsafe_allow_html=True)
        st.markdown(f'<div class="milestone-banner">🚀 {target_country.upper()} PATHWAY: CLASS {target_class}</div>', unsafe_allow_html=True)

        for i, row in df.iterrows():
            month = str(row.get('Month', 'TBD')).upper()
            
            # --- CONTENT SELECTION LOGIC ---
            if target_class == "12th":
                task_name = str(row.get('Phase', 'Requirement'))
                
                # Dynamic mapping for 12th Grade
                if target_country == "USA":
                    details = row.get('USA (Private/Ivies)', 'Check specific university deadlines.')
                elif target_country == "UK":
                    details = row.get('UK (UCAS)', 'Follow UCAS track.')
                elif target_country == "Singapore":
                    details = row.get('Singapore (NUS/NTU)', 'Prepare board predicted scores.')
                elif target_country == "Germany":
                    # Use Singapore data but replace text
                    raw_text = str(row.get('Singapore (NUS/NTU)', 'Check entry requirements.'))
                    details = raw_text.replace("Singapore", "Germany").replace("NUS/NTU", "Public Universities")
                elif target_country == "Australia":
                    details = row.get('Europe / Australia', 'Check GTE requirements.')
                elif target_country == "Canada":
                    # Use Australia data but replace text
                    raw_text = str(row.get('Europe / Australia', 'Check Study Permit requirements.'))
                    details = raw_text.replace("Australia", "Canada")
                else:
                    details = "General international student preparation."
            else:
                # Logic for 9th-11th (General Profile Building)
                task_name = row.get('Task Name', row.get('Phase', 'Activity'))
                details = row.get('Outcome ', 'Building profile milestones.')

            # --- RENDER CARD ---
            # Clean up 'nan' if any
            details = "" if str(details).lower() == 'nan' else details
            
            st.markdown(f"""
                <div class="task-card">
                    <div class="month-tag">{month}</div>
                    <div class="task-title">{task_name}</div>
                    <div class="task-details">{details}</div>
                </div>
                <div class="connector">↓</div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="milestone-banner">🎯 ADMISSION SECURED IN {target_country.upper()}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}. Please check if the 'Class {target_class}' sheet exists in your Excel file.")
else:
    st.error(f"File '{excel_file}' not found.")
