# task1/ingest.py
import pandas as pd
from pathlib import Path

# Import our custom modules
import normalize as norm
from match import build_golden_records
from db import setup_schema

# --- DIRECTORY SETUP ---
# This looks up one level from Task_1 to find the data folder
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'

def extract_and_clean():
    """Reads the real CSVs from the data folder and applies normalize.py functions."""
    print(f"Reading raw files from: {DATA_DIR}...")
    
    # 1. NAUKRI APPLICANTS (Source 1)
    df1 = pd.read_csv(DATA_DIR / 'source1_naukri_applicants.csv')
    df1['Email'] = df1['Email'].str.lower().str.strip()
    df1['Phone'] = df1['Phone'].apply(norm.clean_phone)
    df1['City'] = df1['City'].apply(norm.clean_city)
    df1['Full Name'] = df1['Full Name'].apply(norm.clean_name)
    df1['Applied Date'] = pd.to_datetime(df1['Applied Date'], format='mixed', dayfirst=True, errors='coerce')
    
    # Internal deduplication for Source 1
    df1 = df1.sort_values('Applied Date', ascending=False)
    df1 = df1.drop_duplicates(subset=['Email'], keep='first')
    df1 = df1.drop_duplicates(subset=['Phone'], keep='first')

    # 2. GIG WORKERS (Source 2)
    df2 = pd.read_csv(DATA_DIR / 'source2_gig_workers.csv')
    df2 = df2.apply(norm.fix_gig_shifted_rows, axis=1) # Fix shifted columns
    df2['email_id'] = df2['email_id'].str.lower().str.strip()
    df2['location'] = df2['location'].apply(norm.clean_city)
    df2['rate'] = df2['rate'].apply(norm.clean_hourly_rate)

    # 3. CBNEXUS (Source 3)
    df3 = pd.read_csv(DATA_DIR / 'source3_cbnexus_contacts.csv')
    df3 = df3[df3['Phone Number'] != 'Phone Number'].copy() # Drop embedded header
    df3['Phone Number'] = df3['Phone Number'].apply(norm.clean_phone)
    df3['City'] = df3['City'].apply(norm.clean_city)
    df3['Verified'] = df3['Verified'].apply(norm.clean_boolean)
    df3['Projects Completed'] = pd.to_numeric(df3['Projects Completed'], errors='coerce')

    return df1, df2, df3

def run_pipeline():
    print("=== Starting Golden Record ETL Pipeline ===\n")
    
    # 1. Ensure DB exists & get SQLAlchemy connection engine
    print("1. Validating MySQL Schema...")
    engine = setup_schema()
    
    # 2. Extract & Clean (Applying normalize.py)
    print("\n2. Extracting and Cleaning Data...")
    df1, df2, df3 = extract_and_clean()
    
    # 3. Entity Resolution (Applying match.py)
    print("\n3. Executing Matching Cascade...")
    df_person, df_naukri, df_gig, df_cbnexus = build_golden_records(df1, df2, df3)
    print(f"   -> Successfully merged into {len(df_person)} unique Golden Records.")
    
    # 4. Database Insertion
    print("\n4. Inserting Data into MySQL...")
    
    # Insert Hub Table First (Due to Foreign Key constraints)
    df_person.to_sql('PERSON', con=engine, if_exists='append', index=False)
    print("   -> Inserted PERSON data.")
    
    # Insert Child Tables
    df_naukri.to_sql('NAUKRI_APPLICATION', con=engine, if_exists='append', index=False)
    print("   -> Inserted NAUKRI_APPLICATION data.")
    
    df_gig.to_sql('GIG_WORKER_PROFILE', con=engine, if_exists='append', index=False)
    print("   -> Inserted GIG_WORKER_PROFILE data.")
    
    df_cbnexus.to_sql('CBNEXUS_CONTACT', con=engine, if_exists='append', index=False)
    print("   -> Inserted CBNEXUS_CONTACT data.")
    
    print("\n=== Pipeline Execution Complete! ===")

if __name__ == "__main__":
    run_pipeline()