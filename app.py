import streamlit as st
import pandas as pd
import io

# Set page config
st.set_page_config(
    page_title="Data Clean - Auto Column Purge",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Main Container font overrides */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Outfit', sans-serif;
}

/* Background and container styling */
.header-container {
    background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
    padding: 2.5rem;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    margin-bottom: 2rem;
    text-align: center;
    color: white;
}

.header-container h1 {
    font-weight: 700;
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header-container p {
    color: #94a3b8;
    font-size: 1.1rem;
    font-weight: 300;
}

/* Stats card layout */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.2rem;
    margin: 1.5rem 0 2rem 0;
}

.stat-card {
    background: rgba(30, 41, 59, 0.7);
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    text-align: center;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(8px);
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-3px);
    border-color: rgba(96, 165, 250, 0.5);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
}

.stat-val {
    font-size: 2.25rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-val.removed {
    background: linear-gradient(90deg, #f43f5e, #fb7185);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-lbl {
    font-size: 0.85rem;
    font-weight: 500;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Info Alert box style */
.info-box {
    background: rgba(59, 130, 246, 0.08);
    border-left: 4px solid #3b82f6;
    padding: 1rem 1.5rem;
    border-radius: 0 8px 8px 0;
    margin: 1rem 0;
    font-size: 0.95rem;
    color: #e2e8f0;
}

</style>
""", unsafe_allow_html=True)

# Main layout header
st.markdown("""
<div class="header-container">
    <h1>🧹 Auto Column Purge</h1>
    <p>Upload Excel or CSV files to automatically strip localization headers (@) and remove empty columns.</p>
</div>
""", unsafe_allow_html=True)

# Helper function to check if column has any non-trivial data
def has_data(series):
    non_null = series.dropna()
    if non_null.dtype == object:
        # Convert to string, strip whitespace and check for empty strings
        non_null = non_null.astype(str).str.strip()
        non_null = non_null[non_null != ""]
    return len(non_null) > 0

# Sidebar with explanation and steps
with st.sidebar:
    st.markdown("### 🛠️ Operation Pipeline")
    st.markdown("""
    This utility performs the following cleanup automatically:
    
    1. **Delete Localization Columns**
       Any column with `@` in the header (e.g., `Rate@en_US`) is immediately dropped.
    
    2. **Remove Unused Columns**
       Any column that has no values/data except the header is cleaned.
       
    3. **Excel File Conversion**
       Any uploaded CSV will be downloaded as a beautifully formatted Excel file.
    """)
    st.markdown("---")
    st.markdown("Created by Antigravity AI 🚀")

# File uploader
uploaded_file = st.file_uploader(
    "Choose an Excel (.xlsx, .xls) or CSV (.csv) file",
    type=["xlsx", "xls", "csv"],
    help="Upload the data sheet to clean"
)

if uploaded_file is not None:
    # Read logic based on extension
    file_name = uploaded_file.name
    is_csv = file_name.endswith('.csv')
    
    try:
        with st.spinner("Reading uploaded file..."):
            if is_csv:
                # Read CSV
                df_original = pd.read_csv(uploaded_file)
                sheet_names = None
                selected_sheet = None
            else:
                # Read Excel
                xls = pd.ExcelFile(uploaded_file)
                sheet_names = xls.sheet_names
                if len(sheet_names) > 1:
                    selected_sheet = st.selectbox(
                        "This workbook contains multiple sheets. Choose a sheet to process:",
                        options=sheet_names
                    )
                else:
                    selected_sheet = sheet_names[0]
                df_original = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        
        st.success("File uploaded successfully!")
        
        # Clean processing logic
        with st.spinner("Cleaning dataset columns..."):
            # Step 1: Remove columns containing "@" in header
            cols_at_removed = [col for col in df_original.columns if '@' in str(col)]
            df_no_at = df_original.drop(columns=cols_at_removed)
            
            # Step 2: Remove columns with no data
            cols_no_data = [col for col in df_no_at.columns if not has_data(df_no_at[col])]
            df_cleaned = df_no_at.drop(columns=cols_no_data)
        
        # Calculate stats
        original_cols_cnt = len(df_original.columns)
        at_cols_cnt = len(cols_at_removed)
        empty_cols_cnt = len(cols_no_data)
        final_cols_cnt = len(df_cleaned.columns)
        rows_cnt = len(df_original)
        
        # Display Premium Stats Cards
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-val">{rows_cnt:,}</div>
                <div class="stat-lbl">Total Rows</div>
            </div>
            <div class="stat-card">
                <div class="stat-val">{original_cols_cnt}</div>
                <div class="stat-lbl">Original Columns</div>
            </div>
            <div class="stat-card">
                <div class="stat-val removed">{at_cols_cnt}</div>
                <div class="stat-lbl">"@" Columns Purged</div>
            </div>
            <div class="stat-card">
                <div class="stat-val removed">{empty_cols_cnt}</div>
                <div class="stat-lbl">Empty Columns Purged</div>
            </div>
            <div class="stat-card" style="border-color: rgba(16, 185, 129, 0.4)">
                <div class="stat-val" style="background: linear-gradient(90deg, #10b981, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{final_cols_cnt}</div>
                <div class="stat-lbl">Columns Kept</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Download Option
        st.markdown("### 💾 Export Cleaned File")
        
        # Write df to Excel bytes buffer
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            # If original was Excel with multiple sheets, we might want to clean the active one.
            # But the user asked: "download as excel option and preview data"
            df_cleaned.to_excel(writer, sheet_name=selected_sheet or "Cleaned Data", index=False)
            
        excel_data = excel_buffer.getvalue()
        
        # Propose nice filename
        clean_file_name = file_name.rsplit('.', 1)[0] + "_cleaned.xlsx"
        
        # Center or distinct styled download button
        st.download_button(
            label="📥 Download Cleaned Excel File",
            data=excel_data,
            file_name=clean_file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Click to download the cleaned table as a Microsoft Excel workbook (.xlsx)"
        )
        
        # Previews in tabs
        st.markdown("### 📊 Preview & Compare Data")
        tab1, tab2, tab3 = st.tabs(["✨ Cleaned Data Preview", "📁 Original Data Preview", "🗑️ Purged Columns list"])
        
        with tab1:
            st.markdown(f"**Cleaned DataFrame ({rows_cnt} rows × {final_cols_cnt} columns)**")
            st.dataframe(df_cleaned, width='stretch')
            
        with tab2:
            st.markdown(f"**Original DataFrame ({rows_cnt} rows × {original_cols_cnt} columns)**")
            st.dataframe(df_original, width='stretch')
            
        with tab3:
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown(f"🔴 **Columns with '@' removed ({at_cols_cnt}):**")
                if at_cols_cnt > 0:
                    st.write(cols_at_removed)
                else:
                    st.info("No columns contained '@'")
            with col_r:
                st.markdown(f"🟡 **Empty columns removed ({empty_cols_cnt}):**")
                if empty_cols_cnt > 0:
                    st.write(cols_no_data)
                else:
                    st.info("No empty columns were found")
                    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.info("Please make sure the file format matches Excel or CSV standards.")
else:
    # State when no file is uploaded
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.45); padding: 3rem; border-radius: 12px; border: 1px dashed rgba(255, 255, 255, 0.2); text-align: center; color: #94a3b8;">
        <h3>📥 Upload a file to begin</h3>
        <p>Drop your Excel or CSV file in the slot above to automatically filter localization and empty columns.</p>
    </div>
    """, unsafe_allow_html=True)
