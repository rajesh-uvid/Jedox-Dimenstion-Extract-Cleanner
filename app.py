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
        
        # 1. State initialization/reset on new file
        file_id = f"{file_name}_{selected_sheet}"
        if "processed_state" not in st.session_state or st.session_state.processed_state.get("file_id") != file_id:
            # Run default cleanup immediately (default behavior on first upload)
            cols_at_removed = [col for col in df_original.columns if '@' in str(col)]
            df_no_at = df_original.drop(columns=cols_at_removed)
            cols_no_data = [col for col in df_no_at.columns if not has_data(df_no_at[col])]
            df_cleaned = df_no_at.drop(columns=cols_no_data)
            
            st.session_state.processed_state = {
                "file_id": file_id,
                "df_cleaned": df_cleaned,
                "cols_at_removed": cols_at_removed,
                "cols_no_data": cols_no_data,
                "cols_manual_removed": []
            }

        # 2. Display Configuration Panel (interactive UI styling matching the premium theme)
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.4); padding: 1.25rem 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); margin-top: 1.5rem; margin-bottom: 1rem;">
            <h3 style="margin: 0 0 0.5rem 0; color: #f8fafc; font-size: 1.25rem; font-weight: 600; background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🛠️ Column Cleanup Configuration</h3>
            <p style="margin: 0; color: #94a3b8; font-size: 0.9rem;">Toggle default filters or choose specific columns to delete. All checked and selected columns will be purged on clicking "Run Column Purge".</p>
        </div>
        """, unsafe_allow_html=True)
        
        chk_at_key = f"chk_at_{file_id}"
        chk_empty_key = f"chk_empty_{file_id}"
        multi_key = f"multi_{file_id}"
        
        col_conf_1, col_conf_2 = st.columns([2, 3])
        with col_conf_1:
            remove_at = st.checkbox("Delete '@' localization columns", value=True, key=chk_at_key, help="Remove columns whose headers contain the '@' symbol.")
            remove_empty = st.checkbox("Delete empty columns", value=True, key=chk_empty_key, help="Remove columns that do not contain any non-trivial data.")
        
        with col_conf_2:
            manual_cols = st.multiselect(
                "Select additional columns to delete",
                options=df_original.columns.tolist(),
                default=[],
                key=multi_key,
                help="Search and select any other columns from the original dataset you want to delete."
            )
            
        # Run Column Purge button
        purge_button = st.button("🧹 Run Column Purge", type="primary", use_container_width=True)
        
        if purge_button:
            with st.spinner("Purging columns..."):
                # First apply manual selections
                df_working = df_original.copy()
                cols_manual = manual_cols
                
                # Drop manual columns
                if cols_manual:
                    df_working = df_working.drop(columns=[c for c in cols_manual if c in df_working.columns])
                    
                # Identify '@' columns
                if remove_at:
                    cols_at = [col for col in df_working.columns if '@' in str(col)]
                    df_working = df_working.drop(columns=cols_at)
                    # Relate back to original columns for stats
                    cols_at_removed_stat = [col for col in df_original.columns if '@' in str(col) and col not in cols_manual]
                else:
                    cols_at_removed_stat = []
                    
                # Identify empty columns
                if remove_empty:
                    cols_no_data_stat = [col for col in df_working.columns if not has_data(df_working[col])]
                    df_working = df_working.drop(columns=cols_no_data_stat)
                else:
                    cols_no_data_stat = []
                    
                # Save to state
                st.session_state.processed_state = {
                    "file_id": file_id,
                    "df_cleaned": df_working,
                    "cols_at_removed": cols_at_removed_stat,
                    "cols_no_data": cols_no_data_stat,
                    "cols_manual_removed": cols_manual
                }
                st.success("Successfully purged selected columns and applied clean filters!")
                
        # 3. Retrieve processed data & stats from state
        df_cleaned = st.session_state.processed_state["df_cleaned"]
        cols_at_removed = st.session_state.processed_state["cols_at_removed"]
        cols_no_data = st.session_state.processed_state["cols_no_data"]
        cols_manual_removed = st.session_state.processed_state["cols_manual_removed"]
        
        original_cols_cnt = len(df_original.columns)
        at_cols_cnt = len(cols_at_removed)
        empty_cols_cnt = len(cols_no_data)
        manual_cols_cnt = len(cols_manual_removed)
        final_cols_cnt = len(df_cleaned.columns)
        rows_cnt = len(df_original)
        
        # Display Premium Stats Cards (with 6 cards for added manual deletion stats!)
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
            <div class="stat-card">
                <div class="stat-val removed" style="background: linear-gradient(90deg, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{manual_cols_cnt}</div>
                <div class="stat-lbl">Custom Columns Purged</div>
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
            col_l, col_m, col_r = st.columns(3)
            with col_l:
                st.markdown(f"🔴 **Columns with '@' removed ({at_cols_cnt}):**")
                if at_cols_cnt > 0:
                    st.write(cols_at_removed)
                else:
                    st.info("No columns contained '@' (or deleted manually)")
            with col_m:
                st.markdown(f"🟡 **Empty columns removed ({empty_cols_cnt}):**")
                if empty_cols_cnt > 0:
                    st.write(cols_no_data)
                else:
                    st.info("No empty columns were found")
            with col_r:
                st.markdown(f"🟠 **Custom columns removed ({manual_cols_cnt}):**")
                if manual_cols_cnt > 0:
                    st.write(cols_manual_removed)
                else:
                    st.info("No columns manually selected")
                    
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
