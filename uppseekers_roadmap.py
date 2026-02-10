import streamlit as st
import pandas as pd
import os
from graphviz import Digraph

# --- PAGE CONFIG ---
st.set_page_config(page_title="Admit AI | Snake Roadmap", layout="wide")

def create_snake_roadmap(data, target_class):
    # 'dot' engine is best for hierarchical/snake flows
    dot = Digraph(comment='Admissions Snake', engine='dot')
    
    # Increase DPI for high-res "Zoomed In" look
    dot.attr(rankdir='TB', size='20,20', dpi='300', bgcolor='#1a2a3a')
    
    # Node Styling (Larger fonts and boxes for readability)
    dot.attr('node', shape='rect', style='filled, rounded', 
             fontname='Helvetica-Bold', fontcolor='white', 
             fontsize='16', width='4', height='1.2', penwidth='2')
    
    # Edge Styling (Thicker "Snake" connection)
    dot.attr('edge', color='#4b79a1', penwidth='5', arrowhead='vee', arrowsize='1.2')

    # Color Palette
    phase_color = "#2ecc71" # Green for milestones
    task_color = "#3498db"  # Blue for tasks

    # 1. Start Node (Current Stage)
    dot.node("START", f"CURRENT STAGE\n(Class {target_class})", fillcolor="#e67e22", shape="doubleoctagon")
    
    prev_node = "START"

    for i, row in data.iterrows():
        month = str(row.get('Month', '')).strip()
        task = str(row.get('Task/Milestone', row.get('Task', 'Activity')))
        
        # Clean text: Wrap text for better box fitting
        wrapped_task = task[:40] + "..." if len(task) > 40 else task
        node_id = f"step_{i}"
        
        # Create the Task Node
        label = f"<<B>{month}</B><BR/><FONT POINT-SIZE='12'>{wrapped_task}</FONT>>"
        dot.node(node_id, label, fillcolor=task_color)
        
        # Connect to previous
        dot.edge(prev_node, node_id)
        prev_node = node_id
        
        # Every 4 months, let's assume a "Check-in" milestone to maintain the flow
        if i > 0 and i % 4 == 0:
            milestone_id = f"m_{i}"
            dot.node(milestone_id, "MILESTONE REACHED", fillcolor=phase_color, shape="diamond", fontsize='12')
            dot.edge(prev_node, milestone_id)
            prev_node = milestone_id

    # Final Goal Node
    dot.node("END", "🎯 UNIVERSITY ADMISSION", fillcolor="#9b59b6", shape="star", fontsize='20')
    dot.edge(prev_node, "END")

    return dot

# --- UI ---
st.title("🐍 Admit AI: The Admissions Snake")
st.write("A high-resolution, step-by-step path from your current stage to university admission.")

with st.sidebar:
    st.header("Setup")
    target_class = st.selectbox("Current Class", ["9th", "10th", "11th", "12th"])
    start_month = st.selectbox("Current Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])

excel_file = "Class wise Tentative Flow .xlsx"

if os.path.exists(excel_file):
    try:
        sheet_name = f"Class {target_class}"
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        df.columns = df.columns.str.strip()

        # Filtering logic
        if 'Month' in df.columns:
            mask = df['Month'].str.contains(start_month, case=False, na=False)
            if mask.any():
                start_idx = df[mask].index[0]
                filtered_df = df.iloc[start_idx:].reset_index(drop=True)
            else:
                filtered_df = df

        # Create Graph
        snake_graph = create_snake_roadmap(filtered_df, target_class)
        
        # Render with a specific width to ensure it fills the screen
        st.graphviz_chart(snake_graph, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.error(f"File '{excel_file}' not found.")
