import pandas as pd

excel_path = r"path"
df = pd.read_excel(excel_path)
print("Original Columns Count:", len(df.columns))

# 1. Delete columns where header contains "@"
cols_no_at = [col for col in df.columns if '@' not in str(col)]
df_cleaned1 = df[cols_no_at]
print("Columns after removing '@':", len(df_cleaned1.columns))

# 2. Remove columns with no data except header
def has_data(series):
    non_null = series.dropna()
    # Check if they are empty strings
    if non_null.dtype == object:
        # Convert to string, strip, and filter out empty
        non_null = non_null.astype(str).str.strip()
        non_null = non_null[non_null != ""]
    return len(non_null) > 0

cols_with_data = [col for col in df_cleaned1.columns if has_data(df_cleaned1[col])]
df_cleaned2 = df_cleaned1[cols_with_data]
print("Columns after removing empty ones:", len(df_cleaned2.columns))
print("Remaining columns:", list(df_cleaned2.columns))
