import streamlit as st
import pandas as pd
import os
from graphviz import Digraph

# --- PAGE CONFIG ---
st.set_page_config(page_title="Admit AI | Visual Roadmap", layout="wide")

def create_visual_roadmap(data, student_name):
    # Initialize the graph
    dot = Digraph(comment='Admissions Roadmap', engine='dot')
    dot.attr(rankdir='LR', size='12,12', bgcolor='#1a2a3a') # Dark background like your image
    
    # Global node styles
    dot.attr('node', shape='box', style='filled, rounded', 
             fontname='Helvetica', fontcolor='white', fontsize='11', width='2.5')
    dot.attr('edge', color='#4b79a1', penwidth='3', arrowhead='normal', arrowsize='1.5')

    # Color palette for different phases
    colors = ["#e67e22", "#2ecc71", "#3498db", "#9b59b6", "#f1c40f", "#1abc9c"]
    
    # Create Nodes from Excel Data
    prev_node = None
    for i, row in data.iterrows():
        month = str(row.get('Month', ''))
        task = str(row.get('Task/Milestone', row.get('Task', 'Activity')))
        
        # Clean text for display (limit length)
        display_text = f"{month}\n{task[:50]}..." if len(task) > 50 else f"{month}\n{task}"
        
        node_id = f"node_{i}"
        color = colors[i % len(colors)] # Cycle through colors
        
        dot.node(node_id, display_text, fillcolor=color)
        
        if prev_node:
            dot.edge(prev_node, node_id)
        prev_node = node_id

    return dot

# --- UI INTERFACE ---
st.title("🎨 Admit AI: Visual Admissions Journey")
st.write("Transforming your academic plan into a professional roadmap.")

# Sidebar for Inputs
with st.sidebar:
    st.header("Personalization")
    name = st.text_input("Student Name", "Aspirant")
    target_class = st.selectbox("Current Class", ["9th", "10th", "11th", "12th"])
    start_month = st.selectbox("Current Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])

# Load Excel Logic
excel_file = "Class wise Tentative Flow .xlsx"

if os.path.exists(excel_file):
    try:
        sheet_name = f"Class {target_class}"
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        df.columns = df.columns.str.strip()

        # Filter by Start Month
        if 'Month' in df.columns:
            mask = df['Month'].str.contains(start_month, case=False, na=False)
            if mask.any():
                start_idx = df[mask].index[0]
                filtered_df = df.iloc[start_idx:].reset_index(drop=True)
            else:
                filtered_df = df
        
        # Display Visual Roadmap
        st.subheader(f"The {target_class} Grade Path for {name}")
        
        roadmap_graph = create_visual_roadmap(filtered_df, name)
        
        # Render the diagram in Streamlit
        st.graphviz_chart(roadmap_graph, use_container_width=True)
        
        st.info("💡 The diagram above is generated dynamically from your Excel data. Each block represents a milestone in your journey.")

    except Exception as e:
        st.error(f"Error processing sheet: {e}")
else:
    st.error(f"File '{excel_file}' not found. Ensure it is in your GitHub repository.")
