import streamlit as st
import pandas as pd
import os
from graphviz import Digraph

# --- PAGE CONFIG ---
st.set_page_config(page_title="Admit AI | Premium Roadmap", layout="wide")

# Custom CSS for a better UI
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stHeading h1 { color: #ff4b4b; text-align: center; font-family: 'Helvetica'; }
    </style>
    """, unsafe_allow_html=True)

def create_premium_snake(data, target_class):
    # 'neato' engine allows for specific positioning to create a real "Snake"
    dot = Digraph(comment='Admissions Journey', engine='dot')
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.8', ranksep='0.6', bgcolor='#1a2a3a')
    
    # Premium Node Styling
    dot.attr('node', shape='rect', style='filled, rounded', 
             fontname='Arial Bold', fontcolor='white', 
             fontsize='14', width='3.5', height='1', penwidth='3', color='#4b79a1')
    
    # Edge Styling
    dot.attr('edge', color='#ffffff55', penwidth='4', arrowhead='normal', arrowsize='1')

    # Start Banner
    dot.node("START", f"CURRENT STAGE: CLASS {target_class}", fillcolor="#e67e22", shape="box", width='5')
    
    prev_node = "START"
    
    for i, row in data.iterrows():
        month = str(row.get('Month', '')).upper()
        # Use a secondary column for details if available, otherwise truncate
        task_title = str(row.get('Task/Milestone', row.get('Task', 'Planning')))
        
        node_id = f"step_{i}"
        
        # Elegant HTML Label for clarity
        label = f'<<TABLE BORDER="0" CELLBORDER="0"><TR><TD><B>{month}</B></TD></TR><TR><TD><FONT POINT-SIZE="10">{task_title[:45]}</FONT></TD></TR></TABLE>>'
        
        # Change colors based on progress
        color = "#3498db" if i % 2 == 0 else "#2980b9"
        dot.node(node_id, label, fillcolor=color)
        
        # Connect nodes
        dot.edge(prev_node, node_id)
        prev_node = node_id

    # The Goal
    dot.node("END", "🎓 ADMISSION SECURED", fillcolor="#27ae60", shape="egg", width='4')
    dot.edge(prev_node, "END")

    return dot

# --- APP INTERFACE ---
st.title("🐍 YOUR ADMISSIONS SNAKE ROADMAP")

with st.sidebar:
    st.header("Student Info")
    name = st.text_input("Name", "Student")
    grade = st.selectbox("Current Grade", ["9th", "10th", "11th", "12th"])
    month_start = st.selectbox("Start Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])

excel_file = "Class wise Tentative Flow .xlsx"

if os.path.exists(excel_file):
    try:
        df = pd.read_excel(excel_file, sheet_name=f"Class {grade}")
        df.columns = df.columns.str.strip()

        # Filter logic
        if 'Month' in df.columns:
            mask = df['Month'].str.contains(month_start, case=False, na=False)
            if mask.any():
                df = df.iloc[df[mask].index[0]:].reset_index(drop=True)

        # Generate Graph
        roadmap = create_premium_snake(df, grade)
        
        # DISPLAY SECTION
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.graphviz_chart(roadmap, use_container_width=True)
            
        # Optional: Raw Data for the "Report" feel
        with st.expander("📄 View Detailed Monthly Action Plan"):
            st.table(df)

    except Exception as e:
        st.error(f"Error loading your path: {e}")
else:
    st.error("Excel file missing in the repository!")
