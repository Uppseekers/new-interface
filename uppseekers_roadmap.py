import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Uppseekers Admit AI Roadmap", layout="wide")

class RoadmapPDF(FPDF):
    def header(self):
        # Header Branding
        self.set_fill_color(26, 42, 58) 
        self.rect(0, 0, 210, 35, 'F')
        self.set_font("Arial", 'B', 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, "UPPSEEKERS: ADMIT AI", ln=True, align='C')
        self.set_font("Arial", '', 10)
        self.cell(0, 5, "Personalized University Admissions Roadmap", ln=True, align='C')
        self.ln(15)

    def draw_roadmap_item(self, x, y, month, task, is_last=False):
        # Draw the connection line (The Snake Flow)
        if not is_last:
            self.set_draw_color(75, 121, 161)
            self.set_line_width(1.5)
            self.line(x + 10, y + 15, x + 10, y + 35)
        
        # Draw Node Circle
        self.set_fill_color(230, 126, 34) # Orange from your image
        self.circle(x + 5, y + 2, 10, 'F')
        
        # Text Content
        self.set_xy(x + 20, y)
        self.set_font("Arial", 'B', 11)
        self.set_text_color(26, 42, 58)
        self.cell(0, 10, f"{month.upper()}: {task}", ln=True)

# --- APP LOGIC ---
st.title("🎓 Uppseekers Roadmap Generator")

# Sidebar Inputs
with st.sidebar:
    st.header("Student Details")
    name = st.text_input("Student Name", "Aspirant")
    target_class = st.selectbox("Current Class", ["9th", "10th", "11th", "12th"])
    start_month = st.selectbox("Current Month", [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ])
    intake_year = st.number_input("Target Intake Year", value=2027)

# Load the Excel File
excel_file = "Class wise Tentative Flow .xlsx"

if os.path.exists(excel_file):
    try:
        # Load the specific sheet (e.g., "Class 11th")
        sheet_name = f"Class {target_class}"
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # Data Cleaning: Strip spaces from column names
        df.columns = df.columns.str.strip()
        
        # Filter: Start roadmap from the selected month
        if 'Month' in df.columns:
            # Find index of the selected month
            mask = df['Month'].str.contains(start_month, case=False, na=False)
            if mask.any():
                start_idx = df[mask].index[0]
                filtered_df = df.iloc[start_idx:].reset_index(drop=True)
            else:
                filtered_df = df
        else:
            st.error("Column 'Month' not found in the Excel sheet.")
            filtered_df = df

        st.subheader(f"Timeline for {name} (Class {target_class})")
        st.dataframe(filtered_df, use_container_width=True)

        # PDF Generation
        if st.button("🚀 Generate PDF Roadmap"):
            pdf = RoadmapPDF()
            pdf.add_page()
            
            # Sub-info
            pdf.set_font("Arial", 'I', 10)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 10, f"Prepared for: {name} | Start: {start_month} | Intake: {intake_year}", ln=True)
            pdf.ln(5)

            y_tracker = pdf.get_y()
            for i, row in filtered_df.iterrows():
                month_val = str(row.get('Month', ''))
                task_val = str(row.get('Task/Milestone', row.get('Task', 'Activity')))
                
                # Check for page overflow
                if y_tracker > 250:
                    pdf.add_page()
                    y_tracker = 40
                
                pdf.draw_roadmap_item(20, y_tracker, month_val, task_val, is_last=(i == len(filtered_df)-1))
                y_tracker += 25

            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            
            st.download_button(
                label="📥 Download My Roadmap",
                data=pdf_bytes,
                file_name=f"Uppseekers_{name}_Roadmap.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Error reading the sheet: {e}")
else:
    st.error(f"File '{excel_file}' not found. Please upload it to your GitHub repository.")
