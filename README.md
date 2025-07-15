# 📈 Rolling Average Calculator

A Streamlit web application for calculating rolling peak times from time-series data. This tool helps identify peak activity periods within specified time windows across different groups in your dataset.

## Features

- **Multi-file Support**: Upload and process multiple CSV, Excel, or text files simultaneously
- **Flexible Data Configuration**: 
  - Choose time columns from your data
  - Configure entity counting (row-based or column-based)
  - Set up grouping columns for analysis
  - Select rolling window duration (10-120 minutes)
- **Peak Time Analysis**: Automatically identifies peak activity periods for each group
- **Interactive UI**: Modern, responsive interface with real-time data preview
- **Time Format Support**: Displays results in military time format

## Installation

1. **Clone or download the files**:
   - `rolling_average_calculator.py` - Main application
   - `requirements.txt` - Dependencies
   - `README.md` - This file

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application**:
   ```bash
   streamlit run rolling_average_calculator.py
   ```

2. **Access the web interface**:
   - The app will open in your default browser
   - If it doesn't open automatically, navigate to `http://localhost:8501`

3. **Upload your data**:
   - Support formats: CSV (.csv), Excel (.xlsx), Text (.txt)
   - Multiple files can be uploaded simultaneously

4. **Configure your analysis**:
   - **Header Options**: Specify if first row contains headers
   - **Time Column**: Select the column containing time data (in minutes)
   - **Entity Counting**: Choose between:
     - "Each row is an entity" - Count number of rows
     - "Select column" - Sum values from a specific column
   - **Grouping Columns**: Select columns to group your analysis by
   - **Rolling Window**: Choose the duration for peak calculation (10-120 minutes)

5. **View Results**:
   - Results show peak periods for each group
   - Displays start time, end time, and entity count for peak periods
   - Data is presented in an easy-to-read table format

## Data Format Requirements

Your data should include:
- **Time Column**: Numeric values representing time in minutes from a reference point
- **Optional Grouping Columns**: Categories or identifiers for grouping analysis
- **Optional Entity Count Column**: Numeric column for custom entity counting

### Example Data Structure:
```
Time_Minutes | Location | Department | Count
0           | Building_A | Sales     | 5
15          | Building_A | Sales     | 8
30          | Building_A | Sales     | 12
...
```

## How It Works

1. **Rolling Window Analysis**: The application slides a time window across your data
2. **Entity Counting**: For each window position, counts entities (rows or sum of values)
3. **Peak Detection**: Identifies the time window with maximum entity count for each group
4. **Results Display**: Shows peak period start/end times and entity counts

## Dependencies

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Plotly**: Interactive plotting (imported but can be extended for visualizations)
- **openpyxl**: Excel file support

## Troubleshooting

- **File Upload Issues**: Ensure your file format is supported (CSV, XLSX, TXT)
- **Time Column Errors**: Verify time values are numeric (minutes from reference point)
- **Memory Issues**: For large datasets, consider processing files separately
- **Grouping Errors**: Ensure at least one grouping column is selected if your data has categories

## Browser Compatibility

The application works best with modern browsers:
- Chrome (recommended)
- Firefox
- Safari
- Edge