import pandas as pd
import re
from pathlib import Path
import numpy as np

# --- DIRECTORY SETUP ---
# This dynamically finds the project root by going up one level from the task1 folder
# e.g., from /project_root/task1/cleaner.py -> /project_root/
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'

# --- HELPER FUNCTIONS FOR CLEANING ---

def clean_phone(phone_str):
    """Extracts the 10-digit base number and prepends +91 for standard formatting."""
    if pd.isna(phone_str):
        return None
    digits = re.sub(r'\D', '', str(phone_str))
    if len(digits) >= 10:
        return f"+91{digits[-10:]}"
    return None

def clean_city(city_str):
    """Standardizes city names and forces Title Case."""
    if pd.isna(city_str):
        return None
    c = str(city_str).strip().title()
    mapping = {
        'New Delhi': 'Delhi',
        'Gurugram': 'Gurgaon',
        'Bangalore': 'Bengaluru',
        'Pune ': 'Pune'
    }
    return mapping.get(c, c)

def clean_name(name_str):
    """Standardizes names to Title Case and removes excess whitespace."""
    if pd.isna(name_str): 
        return None
    return " ".join(str(name_str).strip().title().split())

def clean_boolean(val_str):
    """Converts the messy variations of 'Verified' into strict Yes/No strings."""
    if pd.isna(val_str): 
        return None
    v = str(val_str).strip().lower()
    if v in ['y', 'yes', 'true', '1']: 
        return 'Yes'
    if v in ['n', 'no', 'false', '0']: 
        return 'No'
    return None

def clean_hourly_rate(rate_str):
    """Extracts numeric rate and normalizes /month to /hr."""
    if pd.isna(rate_str):
        return None
    r_str = str(rate_str).lower()
    num_match = re.search(r'[\d.]+', r_str)
    if not num_match:
        return None
    amount = float(num_match.group())
    if 'month' in r_str:
        return round(amount / 160, 2) 
    return amount

def fix_gig_shifted_rows(row):
    """Detects if 'Pune' leaked into the status column and corrects the row."""
    if str(row['status']).strip().title() == 'Pune':
        row['location'] = 'Pune'
        row['status'] = 'Unknown'
    return row

# --- MAIN PIPELINE ---

def extract_and_clean():
    print(f"Reading raw files from: {DATA_DIR}")
    
    # 1. PROCESS SOURCE 3 (CBNexus)
    df3 = pd.read_csv(DATA_DIR / 'source3_cbnexus_contacts.csv')
    df3 = df3[df3['Phone Number'] != 'Phone Number'].copy() 
    df3['Phone Number'] = df3['Phone Number'].apply(clean_phone)
    df3['Verified'] = df3['Verified'].apply(clean_boolean)
    df3['City'] = df3['City'].apply(clean_city)
    df3['Projects Completed'] = pd.to_numeric(df3['Projects Completed'], errors='coerce')

    # 2. PROCESS SOURCE 2 (Gig Workers)
    df2 = pd.read_csv(DATA_DIR / 'source2_gig_workers.csv')
    df2 = df2.apply(fix_gig_shifted_rows, axis=1) 
    df2['email_id'] = df2['email_id'].str.lower().str.strip()
    df2['location'] = df2['location'].apply(clean_city)
    df2['rate'] = df2['rate'].apply(clean_hourly_rate)

    # 3. PROCESS SOURCE 1 (Naukri Applicants)
    df1 = pd.read_csv(DATA_DIR / 'source1_naukri_applicants.csv')
    df1['Email'] = df1['Email'].str.lower().str.strip()
    df1['Phone'] = df1['Phone'].apply(clean_phone)
    df1['City'] = df1['City'].apply(clean_city)
    
    df1['Applied Date'] = pd.to_datetime(df1['Applied Date'], format='mixed', dayfirst=True, errors='coerce')
    
    df1 = df1.sort_values('Applied Date', ascending=False)
    df1 = df1.drop_duplicates(subset=['Email'], keep='first')
    df1 = df1.drop_duplicates(subset=['Phone'], keep='first')

    print("Cleaning complete.")
    return df1, df2, df3

# if __name__ == "__main__":
#     naukri_clean, gig_clean, cbnexus_clean = extract_and_clean()
    
#     # Save the cleaned files back into the data directory
#     naukri_clean.to_csv(DATA_DIR / 'cleaned_source1.csv', index=False)
#     gig_clean.to_csv(DATA_DIR / 'cleaned_source2.csv', index=False)
#     cbnexus_clean.to_csv(DATA_DIR / 'cleaned_source3.csv', index=False)
    
#     print("Saved cleaned files to the data/ folder. Ready for Step 2 (Deduplication).")
# --- TERMINAL TESTING BLOCK ---
if __name__ == "__main__":
    print("--- Testing Normalization Functions ---\n")
    
    print("1. Testing clean_phone:")
    for p in ['9000000254', '919000000254', '+91-9000000131', np.nan]:
        print(f"   '{p}' -> {clean_phone(p)}")
    
    print("\n2. Testing clean_city:")
    for c in ['Pune ', 'New Delhi', 'Gurugram', 'GURGAON', np.nan]:
        print(f"   '{c}' -> {clean_city(c)}")
    
    print("\n3. Testing clean_hourly_rate:")
    for r in ['1415/hr', '64000/month', np.nan]:
        print(f"   '{r}' -> {clean_hourly_rate(r)}")
        
    print("\n4. Testing fix_gig_shifted_rows:")
    row_bad = {'location': np.nan, 'status': 'Pune'}
    print(f"   {row_bad} -> {fix_gig_shifted_rows(row_bad)}")