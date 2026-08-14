# task1/match.py
import pandas as pd
import numpy as np

def build_golden_records(df1, df2, df3, start_id=1):
    """
    Executes the Entity Resolution cascade.
    Expects df1, df2, df3 to already have normalized columns (clean emails, phones, etc.)
    Returns 4 Pandas DataFrames ready for database insertion.
    """
    persons_dict = {}
    email_to_id = {}
    phone_to_id = {}
    
    naukri_records = []
    gig_records = []
    cbnexus_records = []
    
    current_person_id = start_id

    # --- 1. Process Source 1 (Naukri) - The Bridge ---
    for _, row in df1.iterrows():
        pid = current_person_id
        email = row.get('Email')
        phone = row.get('Phone')
        
        persons_dict[pid] = {
            'person_id': pid,
            'full_name_normalized': row.get('Full Name'),
            'primary_email': email,
            'phone_normalized': phone,
            'primary_city': row.get('City'),
            'merged_sources': ['source1']
        }
        
        # Populate lookup dictionaries
        if pd.notna(email): email_to_id[email] = pid
        if pd.notna(phone): phone_to_id[phone] = pid
        
        naukri_records.append({
            'person_id': pid,
            'skills': row.get('Skills'),
            'experience_years': row.get('Experience (Years)'),
            'current_ctc': row.get('Current CTC'),
            'applied_date': row.get('Applied Date')
        })
        current_person_id += 1

    # --- 2. Process Source 2 (Gig Workers) ---
    for _, row in df2.iterrows():
        email = row.get('email_id')
        
        if pd.notna(email) and email in email_to_id:
            # MATCH FOUND: Link to existing person
            pid = email_to_id[email]
            if 'source2' not in persons_dict[pid]['merged_sources']:
                persons_dict[pid]['merged_sources'].append('source2')
        else:
            # NO MATCH: Create new person
            pid = current_person_id
            persons_dict[pid] = {
                'person_id': pid,
                'full_name_normalized': row.get('worker_name'),
                'primary_email': email,
                'phone_normalized': None,
                'primary_city': row.get('location'),
                'merged_sources': ['source2']
            }
            if pd.notna(email): email_to_id[email] = pid
            current_person_id += 1
            
        gig_records.append({
            'person_id': pid,
            'skill_tags': row.get('skill_tags'),
            'rate_normalized': row.get('rate'),
            'status': row.get('status')
        })

    # --- 3. Process Source 3 (CBNexus) ---
    for _, row in df3.iterrows():
        phone = row.get('Phone Number')
        
        if pd.notna(phone) and phone in phone_to_id:
            # MATCH FOUND: Link to existing person
            pid = phone_to_id[phone]
            if 'source3' not in persons_dict[pid]['merged_sources']:
                persons_dict[pid]['merged_sources'].append('source3')
            
            # Data Enrichment: If the existing person is missing a city, grab it from here
            if pd.isna(persons_dict[pid]['primary_city']):
                persons_dict[pid]['primary_city'] = row.get('City')
        else:
            # NO MATCH: Create new person
            pid = current_person_id
            persons_dict[pid] = {
                'person_id': pid,
                'full_name_normalized': row.get('Name'),
                'primary_email': None,
                'phone_normalized': phone,
                'primary_city': row.get('City'),
                'merged_sources': ['source3']
            }
            if pd.notna(phone): phone_to_id[phone] = pid
            current_person_id += 1
            
        cbnexus_records.append({
            'person_id': pid,
            'verified': row.get('Verified'),
            'projects_completed': row.get('Projects Completed')
        })

    # Format 'merged_sources' array into a comma-separated string for MySQL
    for pid in persons_dict:
        persons_dict[pid]['merged_sources'] = ", ".join(persons_dict[pid]['merged_sources'])

    # Return exactly 4 DataFrames mapping directly to our 4 MySQL tables
    return (
        pd.DataFrame(list(persons_dict.values())), 
        pd.DataFrame(naukri_records), 
        pd.DataFrame(gig_records), 
        pd.DataFrame(cbnexus_records)
    )

# --- TERMINAL TESTING BLOCK ---
if __name__ == "__main__":
    print("--- Testing Matching Cascade Logic ---\n")
    
    # 1. Create Fake Cleaned Data
    # Naukri (The Bridge): Has both email and phone
    df1_mock = pd.DataFrame([{
        'Full Name': 'John Doe', 'Email': 'john@example.com', 'Phone': '+919999999999', 
        'City': 'Pune', 'Skills': 'Python', 'Experience (Years)': 2, 
        'Current CTC': 500000, 'Applied Date': '2026-01-01'
    }])
    
    # Gig Workers: Has ONLY email (Should merge with John Doe based on email)
    # Plus one new unmatched person (Jane)
    df2_mock = pd.DataFrame([
        {'worker_name': 'John D', 'email_id': 'john@example.com', 'location': 'Pune', 'rate': 500, 'status': 'Active', 'skill_tags': 'sql'},
        {'worker_name': 'Jane Smith', 'email_id': 'jane@example.com', 'location': 'Delhi', 'rate': 600, 'status': 'Active', 'skill_tags': 'java'}
    ])
    

    # CBNexus: Has ONLY phone (Should merge with John Doe based on phone)
    # Plus one new unmatched person (Bob)
    df3_mock = pd.DataFrame([
        {'Name': 'J Doe', 'Phone Number': '+919999999999', 'City': 'Pune', 'Verified': 'Y', 'Projects Completed': 5},
        {'Name': 'Bob', 'Phone Number': '+918888888888', 'City': 'Gurgaon', 'Verified': 'N', 'Projects Completed': 1}
    ])
    
    # 2. Run the Engine
    df_person, df_naukri, df_gig, df_cbnexus = build_golden_records(df1_mock, df2_mock, df3_mock)
    
    # 3. Print Results
    print("HUB TABLE (PERSON):")
    print("Notice how John Doe became a single record (person_id = 1) containing all 3 sources.")
    print(df_person[['person_id', 'full_name_normalized', 'primary_email', 'phone_normalized', 'merged_sources']].to_string(index=False))
    
    print("\nCHILD TABLE (NAUKRI):")
    print(df_naukri[['person_id', 'skills', 'experience_years']].to_string(index=False))
    
    print("\nCHILD TABLE (GIG WORKERS):")
    print(df_gig[['person_id', 'skill_tags', 'rate_normalized']].to_string(index=False))
    
    print("\nCHILD TABLE (CBNEXUS):")
    print(df_cbnexus[['person_id', 'verified', 'projects_completed']].to_string(index=False))