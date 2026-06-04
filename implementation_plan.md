# Streamlit Excel and CSV Data Cleaner App

Create a responsive and visually premium Streamlit application that allows users to upload Excel (`.xlsx`, `.xls`) or CSV (`.csv`) files, automatically applies two specific cleaning rules, previews the comparison between original and cleaned data, and exports the results as a new Excel file.

## Cleaning Rules
1. **Remove Columns with `@` in Header**: Any column whose header (converted to string) contains the `@` symbol is removed.
2. **Remove Empty Columns**: Any column that has no data (i.e., contains only null, NaN, or whitespace-only/empty string values, excluding the header) is removed.

---

## User Review Required

> [!NOTE]
> **Theme & Aesthetics**: To make the interface look premium, we will inject a custom modern layout with CSS. It will include:
> - A stylish glassmorphic header card with gradient background.
> - An interactive file dropzone styling.
> - Metrics cards displaying stats (e.g., number of columns removed, rows processed, columns kept).
> - Responsive tables comparing Original vs. Cleaned Data.
> - Highlighting of removed columns in the Original preview.

---

## Proposed Changes

### [Streamlit Web Application]

#### [NEW] [app.py](file:///c:/Users/rajes/Downloads/New%20folder%20(3)/app.py)
Create the main Streamlit application code:
- Import `streamlit`, `pandas`, and `openpyxl`/`io`.
- Define a beautiful custom layout with custom CSS (modern typography, gradient borders, glowing hover effects).
- Create a file uploader that accepts `.csv`, `.xlsx`, and `.xls`.
- Implement robust Excel reading, including sheet selection if a workbook contains multiple sheets.
- Implement the cleaning functions:
  - Identify columns containing `@`.
  - Identify columns containing no non-trivial data.
  - Track stats: count of columns removed by each rule.
- Display a statistics dashboard using modern CSS cards.
- Show previews of original vs. cleaned data in styled tabs.
- Provide a download button that exports the cleaned data as a `.xlsx` Excel file (using `BytesIO` and `openpyxl`).

---

## Verification Plan

### Manual Verification
1. Run the Streamlit application using `streamlit run app.py`.
2. Open the browser to the local server URL (usually `http://localhost:8501`).
3. Upload the provided spreadsheet `Accounts_PL (1).xlsx`.
4. Select the `Accounts_PL` sheet (if prompted).
5. Verify the dashboard metrics:
   - Original columns: 175
   - Columns with `@` removed: 80
   - Empty columns removed: 30
   - Remaining columns: 65
6. Check that the preview shows the cleaned columns correctly.
7. Download the cleaned file as Excel and check that it opens correctly in Excel or Pandas.
