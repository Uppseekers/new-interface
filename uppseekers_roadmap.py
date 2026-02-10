import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

# --- CONFIG ---
st.set_page_config(page_title="Admit AI Roadmap Generator", layout="centered")

def generate_pdf(data, student_name, student_class, intake_year):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_fill_color(26, 42, 58) # Dark blue from your image
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 20, f"Roadmap for {student_name}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Class: {student_class} | Target Intake: {intake_year}", ln=True, align='C')
    
    pdf.ln(20)
    
    # Roadmap Drawing Logic
    pdf.set_text_color(0, 0, 0)
    x_pos = 20
    y_pos = 60
    
    for index, row in data.iterrows():
        # Draw Box
        pdf.set_draw_color(75, 121, 161)
        pdf.set_line_width(1)
        pdf.set_fill_color(240, 240, 240)
        pdf.rect(x_pos, y_pos, 170, 25, 'FD')
        
        # Month & Task
        pdf.set_font("Arial", 'B', 11)
        pdf.text(x_pos + 5, y_pos + 8, f"{row['Month']} - {row['Task/Milestone']}")
        
        pdf.set_font("Arial", size=9)
        # Assuming your CSV has a 'Description' or 'Details' column
        detail = str(row.get('Details', 'Focus on profile building and academics.'))
        pdf.text(x_pos + 5, y_pos + 18, detail[:100]) 
        
        y_pos += 35 # Move down for next task
        
        # Add new page if list is long
        if y_pos > 250:
            pdf.add_page()
            y_pos = 20

    return pdf.output(dest='S').encode('latin-1')

# --- STREAMLIT UI ---
st.title("🎓 Uppseekers: Personalized Roadmap")
st.write("Generate your university admission timeline based on your current grade.")

with st.form("user_details"):
    name = st.text_input("Student Name")
    grade = st.selectbox("Select Current Class", ["9th", "10th", "11th", "12th"])
    start_month = st.selectbox("Current Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    intake = st.number_input("Target Intake Year", min_value=2026, max_value=2030, value=2027)
    
    submit = st.form_submit_button("Generate Roadmap")

if submit:
    # Load corresponding CSV
    file_path = f"Class wise Tentative Flow .xlsx - Class {grade}.csv"
    
    try:
        df = pd.read_csv(file_path)
        
        # Filter logic: find the starting month and show subsequent tasks
        # (This assumes your CSV has a column named 'Month')
        if 'Month' in df.columns:
            # Simple slice: show all tasks from the selected month onwards
            start_idx = df[df['Month'].str.contains(start_month, case=False, na=False)].index
            if not start_idx.empty:
                filtered_df = df.iloc[start_idx[0]:]
            else:
                filtered_df = df
        else:
            filtered_df = df

        st.success(f"Roadmap generated for Class {grade}!")
        st.dataframe(filtered_df) # Show preview

        pdf_bytes = generate_pdf(filtered_df, name, grade, intake)
        
        st.download_button(
            label="📩 Download PDF Roadmap",
            data=pdf_bytes,
            file_name=f"{name}_Roadmap.pdf",
            mime="application/pdf"
        )
    except FileNotFoundError:
        st.error(f"Data file for Class {grade} not found. Please ensure the CSV is in the repository.")
