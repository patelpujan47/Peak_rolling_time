import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO
import base64

# Set page config
st.set_page_config(
    page_title="Rolling Average Calculator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stCheckbox > label,
    .stSelectbox > label,
    .stRadio > label,
    .stMultiSelect > label {
        font-size: 20px;
        font-weight: bold;
        font-weight: 600;
    }
    .stSelectbox > div > div > select {
        background-color: #f0f2f6;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .upload-section {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
</style>
""", unsafe_allow_html=True)

def minutes_to_time(time_in_min, military_time=True):
    hours = time_in_min // 60
    minutes = time_in_min % 60
    if military_time:
        return f"{int(hours):02d}:{int(minutes):02d}"
    else:
        suffix = "AM" if hours < 12 or hours == 24 else "PM"
        hours_12 = hours % 12
        hours_12 = 12 if hours_12 == 0 else hours_12
        return f"{int(hours_12):02d}:{int(minutes):02d} {suffix}"

def rolling_peak_calc(df, time_col, group_cols, entity_col=None, rolling_window = 60, military_time=True):
    try:
        results = []

        for group_values, group_df in df.groupby(group_cols):
            time_series = group_df[time_col]
            min_time = int(time_series.min())
            max_time = int(time_series.max())

            for start in range(min_time, max_time - rolling_window + 1):
                end = start + rolling_window

                # Create a mask for rows in the time window
                mask = (time_series >= start) & (time_series < end)

                # If entity column count is None, count rows; else, sum values
                if entity_col is None:
                    count = mask.sum()
                else:
                    count = group_df.loc[mask, entity_col].sum()

                # Ensure group_values is a tuple (even for a single group)
                if not isinstance(group_values, tuple):
                    group_values = (group_values,)

                result_row = dict(zip(group_cols, group_values))
                result_row.update({
                    'bin_start': start,
                    'bin_end': end,
                    'entities': count
                })
                results.append(result_row)

        results_df = pd.DataFrame(results)

        #convert min to time
        results_df['bin_start_time'] = results_df['bin_start'].apply(lambda x: minutes_to_time(x, military_time))
        results_df['bin_end_time']   = results_df['bin_end'].apply(lambda x: minutes_to_time(x, military_time))
        
        return results_df
        # For each group, get the row(s) with the maximum count
        #max_bins_per_group = (results_df.loc[results_df.groupby(group_cols)['entities'].idxmax()].reset_index(drop=True)[[*group_cols, 'entities', 'bin_start_time', 'bin_end_time']])
        #return max_bins_per_group
    
    except Exception as e:
        st.error(f"Error calculating peak rolling time: {str(e)}")
        return None

# Main app
#st.title("")
st.markdown("<h1 style='text-align: center;'>📈 Rolling Average Calculator</h1>", unsafe_allow_html=True)

# File upload section
st.markdown("<h2 style='text-align: center;'>📂 Upload Your Data</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    uploaded_files = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'txt'],
        help="Supported formats: CSV (.csv), Excel (.xlsx), or Text (.txt) files with numeric data",
        accept_multiple_files=True
    )
    #use_header = st.checkbox("First row is header", value=True)
    #header_option = 0 if use_header else None

    if uploaded_files:
        for file in uploaded_files:
            st.success(f"✅ File `{file.name}` uploaded successfully!")
            #st.write(f"**File name:** {file.name}")
            #st.write(f"**File size:** {file.size} bytes")
            #st.write(f"**File type:** {file.type}")
    else:
        st.info("👆 Please upload a file to get started")

    # Show file details if uploaded
    if uploaded_files:
        st.markdown("<h3 style='text-align: center;'>📊 File Preview</h3>", unsafe_allow_html=True)

    # Initialize data dictionary and configuration dictionary
    data_dict = {}
    config_dict = {}

    for file in uploaded_files:
        st.markdown(f"### 📁 `{file.name}`")
        
        use_header = st.checkbox(
            f"First Row as Header for `{file.name}`",
            value=True,
            key=f"use_header_{file.name}"
        )
        header_option = 0 if use_header else None

        try:
            # Read and display the file based on its type
            if file.name.endswith('.csv'):
                df = pd.read_csv(file, header=header_option)
                st.write("**CSV file loaded successfully!**")
                
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file, header=header_option)
                st.write("**Excel file loaded successfully!**")
                
            elif file.name.endswith('.txt'):
                # Read text file
                df = pd.read_csv(file, header=header_option)
                st.write("**Text file loaded successfully!**")
            
            #Preview
            st.dataframe(df.head(), use_container_width=True)
            st.write(f"**Shape:** {df.shape[0]} rows, {df.shape[1]} columns")
            
            # --- 🕒 Select time column ---
            all_columns = df.columns.tolist()

            time_col_key = st.selectbox(
                f"🕒 Column Number of Time Field for `{file.name}`",
                options=all_columns,
                key=f"timecol_{file.name}"
            )

            # -- Select entity column --
            # Let user choose how to count entities
            count_mode = st.radio(
                f"🧮 How should we count entities in `{file.name}`?",
                options=["Each row is an entity", "Select 'Number of Entities' column"],
                key=f"countmode_{file.name}"
            )
            
            # If user selects to use a specific column for counting
            entity_col_key = None
            if count_mode == "Select 'Number of Entities' column":
                entity_col_key = st.selectbox(
                    f"📊 Select Entity Count Column for `{file.name}`",
                    options=all_columns,
                    key=f"entitycol_{file.name}"
                )

            # -- Select grouping columns --
            grouping_cols = st.multiselect(
            f"🧱 Grouping column(s) for `{file.name}`",
            options=all_columns,
            default=[],
            key=f"groupcols_{file.name}"
            )

            #Select Duration of Peak Time
            rolling_window_min = st.selectbox(
                "🕒 Select Duration of Peak Time (in minutes)",
                options=[10, 15, 20, 30, 60, 120],
                index=2,  # default to 20 minutes
                key=f"rollwin_{file.name}"
            )

            # Store file and configuration
            data_dict[file.name] = df
            config_dict[file.name] = {
            'time_col': time_col_key,
            'count_mode': count_mode,
            'entity_col': entity_col_key,
            'grouping_cols': grouping_cols,
            'rolling_window_min': rolling_window_min
            }

        except Exception as e:
            st.error(f"Error reading `{file.name}`: {str(e)}")
    
    if data_dict and config_dict:
    # Check if all files have complete configurations
        all_configs_complete = True
        incomplete_files = []
        
        for file_name in data_dict.keys():
            if file_name not in config_dict:
                all_configs_complete = False
                incomplete_files.append(file_name)
            else:
                config = config_dict[file_name]
                # Check if all required fields are present
                if not all([
                    config.get('time_col'),
                    config.get('count_mode'),
                    config.get('rolling_window_min') is not None
                ]):
                    all_configs_complete = False
                    incomplete_files.append(file_name)

        if all_configs_complete:
            st.markdown("<h2 style='text-align: center;'>📊 Results</h2>", unsafe_allow_html=True)

        for file_name, df in data_dict.items():
            st.markdown(f"### 📈 Results for `{file_name}`")

            # Get configuration for this file
            config = config_dict[file_name]
            time_col_key = config['time_col']
            entity_col_key = config['entity_col']
            grouping_cols = config['grouping_cols']
            rolling_window_min = config['rolling_window_min']

            # Calculate rolling peak
            peak_df = rolling_peak_calc(df=df, time_col=time_col_key, group_cols=grouping_cols, entity_col=entity_col_key, rolling_window=rolling_window_min)

            if peak_df is not None:
                max_bins_per_group = (
                    peak_df.loc[peak_df.groupby(grouping_cols)['entities'].idxmax()]
                    .reset_index(drop=True)
                    [[*grouping_cols, 'bin_start_time', 'bin_end_time', 'entities']]
                )

                # Rename columns
                max_bins_per_group = max_bins_per_group.rename(columns={
                    'bin_start_time': 'Peak_Period_Start',
                    'bin_end_time': 'Peak_Period_End',
                    'entities': 'Entities_Count'
                })

                # Display result
                st.dataframe(max_bins_per_group, use_container_width=True)