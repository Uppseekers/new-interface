import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Admit AI | Snake Roadmap", layout="wide")

# --- CUSTOM CSS FOR THE SNAKE & CARDS ---
st.markdown("""
<style>
    /* Main Container */
    .roadmap-wrapper {
        background-color: #0f172a;
        padding: 40px;
        border-radius: 20px;
        font-family: 'Inter', sans-serif;
    }
    
    /* The Snake Path Line */
    .roadmap-container {
        display: flex;
        flex-direction: column;
        gap: 30px;
        position: relative;
    }

    /* Milestone Header */
    .milestone-banner {
        background: linear-gradient(90deg, #3b82f6, #2563eb);
        color: white;
        padding: 20px;
        text-align: center;
        border-radius: 15px;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 1px;
        margin: 40px 0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }

    /* Task Card Design */
    .task-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-left: 6px solid #fbbf24;
        padding: 20px;
        border-radius: 12px;
        position: relative;
        transition: transform 0.2s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .task-card:hover {
        transform: translateY(-5px);
        background: #233044;
    }

    .month-tag {
        background: #fbbf24;
        color: #1e293b;
        font-weight: 800;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 12px;
        text-transform: uppercase;
        margin-bottom: 10px;
        display: inline-block;
    }

    .task-title {
        color: #f8fafc;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .task-details {
        color: #94a3b8;
        font-size: 14px;
        line-height: 1.6;
    }

    .detail-item {
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid #334155;
        font-style: italic;
        color: #38bdf8;
    }

    /* Connection Arrow */
    .connector {
        text-align: center;
        color: #334155;
        font-size: 24px;
        margin: -10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- APP LOGIC ---
st.title("🐍 Admit AI: Detailed Journey Roadmap")

with st.sidebar:
    st.header("1. Student Details")
    name = st.text_input("Student Name", "Aspirant")
    target_class = st.selectbox("Current Class", ["9th", "10th", "11th", "12th"])
    start_month = st.selectbox("Current Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])

excel_file = "Class wise Tentative Flow .xlsx"

if os.path.exists(excel_file):
    try:
        # Load the right sheet
        df = pd.read_excel(excel_file, sheet_name=f"Class {target_class}")
        df.columns = [c.strip() for c in df.columns]

        # Filter for Start Month
        if 'Month' in df.columns:
            mask = df['Month'].str.contains(start_month, case=False, na=False)
            if mask.any():
                df = df.iloc[df[mask].index[0]:].reset_index(drop=True)

        # --- DRAWING THE ROADMAP ---
        st.markdown('<div class="roadmap-wrapper">', unsafe_allow_html=True)
        st.markdown(f'<div class="milestone-banner">🚀 START: CLASS {target_class} JOURNEY</div>', unsafe_allow_html=True)
        
        for i, row in df.iterrows():
            month = str(row.get('Month', 'Unknown')).upper()
            
            # Logic to handle different column names between Class 9-11 and Class 12
            if target_class == "12th":
                task_name = row.get('Phase', 'Admissions Phase')
                # Combine multiple region details for Class 12
                details = f"<b>USA:</b> {row.get('USA (Private/Ivies) ', 'N/A')}<br><b>UK:</b> {row.get('UK (UCAS) ', 'N/A')}"
                additional = f"Singapore/Europe: {row.get('Singapore (NUS/NTU)', '')}"
            else:
                task_name = row.get('Task Name', row.get('Phase', 'Milestone'))
                details = row.get('Outcome ', 'Building profile and academic excellence.')
                additional = row.get('Additional Info', '')

            # Render Card
            st.markdown(f"""
                <div class="task-card">
                    <div class="month-tag">{month}</div>
                    <div class="task-title">{task_name}</div>
                    <div class="task-details">{details}</div>
                    {"<div class='detail-item'>💡 " + str(additional) + "</div>" if str(additional) != 'nan' and additional else ""}
                </div>
                <div class="connector">↓</div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="milestone-banner">🎯 GOAL: UNIVERSITY ADMISSION SECURED</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Download Section
        st.sidebar.markdown("---")
        st.sidebar.subheader("2. Export Report")
        csv = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("Download Data (CSV)", csv, f"{name}_roadmap.csv", "text/csv")

    except Exception as e:
        st.error(f"Error loading your data: {e}")
else:
    st.error(f"File '{excel_file}' not found in the repository.")
