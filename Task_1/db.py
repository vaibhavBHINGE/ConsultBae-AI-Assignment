# task1/db.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, Column, Integer, String, Float, Boolean, Date, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import declarative_base, relationship

load_dotenv()

Base = declarative_base()

# --- 1. THE HUB TABLE (Updated for Task 1 & Task 2) ---
class Person(Base):
    __tablename__ = 'PERSON'
    
    person_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name_normalized = Column(String(255))
    primary_email = Column(String(255), unique=True)
    phone_normalized = Column(String(50), unique=True)
    primary_city = Column(String(100))
    merged_sources = Column(String(255))
    
    # ADDED FOR TASK 2: Stores the AI-generated skill category from the LLM
    llm_skill_category = Column(String(255), nullable=True)

    # Relationships to child tables
    naukri_apps = relationship("NaukriApplication", back_populates="person", cascade="all, delete-orphan")
    gig_profiles = relationship("GigWorkerProfile", back_populates="person", cascade="all, delete-orphan")
    cbnexus_contacts = relationship("CbNexusContact", back_populates="person", cascade="all, delete-orphan")
    audio_submissions = relationship("AudioSubmission", back_populates="person", cascade="all, delete-orphan")


# --- 2. SOURCE 1 CHILD TABLE ---
class NaukriApplication(Base):
    __tablename__ = 'NAUKRI_APPLICATION'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('PERSON.person_id', ondelete='CASCADE'))
    skills = Column(Text)
    experience_years = Column(Float)
    current_ctc = Column(DECIMAL(12, 2))
    applied_date = Column(Date)
    source_file = Column(String(255), default='source1_naukri_applicants.csv')

    person = relationship("Person", back_populates="naukri_apps")


# --- 3. SOURCE 2 CHILD TABLE ---
class GigWorkerProfile(Base):
    __tablename__ = 'GIG_WORKER_PROFILE'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('PERSON.person_id', ondelete='CASCADE'))
    skill_tags = Column(Text)
    rate_normalized = Column(DECIMAL(10, 2))
    status = Column(String(50))
    source_file = Column(String(255), default='source2_gig_workers.csv')

    person = relationship("Person", back_populates="gig_profiles")


# --- 4. SOURCE 3 CHILD TABLE ---
class CbNexusContact(Base):
    __tablename__ = 'CBNEXUS_CONTACT'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('PERSON.person_id', ondelete='CASCADE'))
    verified = Column(String(5))
    projects_completed = Column(Integer)
    source_file = Column(String(255), default='source3_cbnexus_contacts.csv')

    person = relationship("Person", back_populates="cbnexus_contacts")


# --- 5. AUDIO SUBMISSION TABLE (ADDED FOR TASK 3) ---
class AudioSubmission(Base):
    __tablename__ = 'AUDIO_SUBMISSION'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('PERSON.person_id', ondelete='CASCADE'))
    file_path = Column(String(500))
    duration_sec = Column(Float)
    sample_rate = Column(Integer)
    bitrate_kbps = Column(Integer)
    loudness_db = Column(Float)

    person = relationship("Person", back_populates="audio_submissions")


# --- DATABASE SETUP LOGIC ---

def get_engine(include_db=True):
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASS", "")
    host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "consultbae_db")
    
    if include_db:
        url = f"mysql+pymysql://{user}:{password}@{host}/{db_name}"
    else:
        url = f"mysql+pymysql://{user}:{password}@{host}/"
        
    return create_engine(url)

def setup_schema():
    db_name = os.getenv("DB_NAME", "consultbae_db")
    
    engine_server = get_engine(include_db=False)
    with engine_server.connect() as conn:
        print(f"1. Checking for database: {db_name}...")
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
    
    engine_db = get_engine(include_db=True)
    print("2. Pushing updated ORM tables (Task 1, 2, & 3 schema) to MySQL...")
    Base.metadata.create_all(engine_db)
    
    print("3. Schema generation complete!")
    return engine_db

if __name__ == "__main__":
    setup_schema()