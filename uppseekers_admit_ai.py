import streamlit as st
import pandas as pd

# ... [Keep REGIONAL_WEIGHTS and CATEGORIES from previous code] ...

@st.cache_data
def load_and_detect_index():
    try:
        q_idx = pd.read_excel("University Readiness_new (3) (1).xlsx", sheet_name="Sheet1")
        b_idx = pd.read_excel("Benchmarking_USA (3) (2) (1).xlsx", sheet_name="Sheet1")
        
        # Standardize column names (lowercase and no spaces)
        q_idx.columns = q_idx.columns.str.strip()
        b_idx.columns = b_idx.columns.str.strip()
        
        # Logic to find the right column even if the name varies
        possible_stream_names = ['Stream', 'Course', 'Set', 'Subject', 'Course Name']
        detected_col = None
        
        for col in q_idx.columns:
            if col in possible_stream_names:
                detected_col = col
                break
        
        if not detected_col:
            # Fallback: Use the first column if no match found
            detected_col = q_idx.columns[0]
            
        return q_idx, b_idx, detected_col
    except Exception as e:
        st.error(f"Could not read index files: {e}")
        return None, None, None

q_index, b_index, stream_col = load_and_detect_index()

if q_index is not None:
    st.sidebar.success(f"Detected mapping column: '{stream_col}'")
    
    # Get unique list from the detected column
    streams = q_index[stream_col].unique().tolist()
    selected_stream = st.sidebar.selectbox("Select Student Stream", streams)
    
    # Locate the file name in the index
    # Looking for a column that sounds like 'File' or 'CSV' or 'Path'
    file_col = [c for c in q_index.columns if 'File' in c or 'Path' in c or 'Sheet' in c]
    file_col = file_col[0] if file_col else q_index.columns[1] # Fallback to 2nd column
    
    q_file_name = q_index[q_index[stream_col] == selected_stream][file_col].values[0]
    
    # Now load the specific data file
    # If the index says 'set_business.csv', this loads that specific file
    df_q = pd.read_csv(q_file_name)
    # ... proceed with the rest of the profiling logic ...
