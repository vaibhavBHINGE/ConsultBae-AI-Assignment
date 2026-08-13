# task1/db.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, Column, Integer, String, Float, Boolean, Date, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import declarative_base, relationship

load_dotenv()

Base = declarative_base()

# --- 1. THE HUB TABLE ---
class Person(Base):
    __tablename__ = 'PERSON'
    
    # Primary Key
    person_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Fields
    full_name_normalized = Column(String(255))
    primary_email = Column(String(255), unique=True)
    phone_normalized = Column(String(50), unique=True)
    primary_city = Column(String(100))
    merged_sources = Column(String(255))

    # Relationships (Links to the child tables)
    naukri_apps = relationship("NaukriApplication", back_populates="person", cascade="all, delete-orphan")
    gig_profiles = relationship("GigWorkerProfile", back_populates="person", cascade="all, delete-orphan")
    cbnexus_contacts = relationship("CbNexusContact", back_populates="person", cascade="all, delete-orphan")


# --- 2. SOURCE 1 CHILD TABLE ---
class NaukriApplication(Base):
    __tablename__ = 'NAUKRI_APPLICATION'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Foreign Key pointing to PERSON.person_id
    person_id = Column(Integer, ForeignKey('PERSON.person_id', ondelete='CASCADE'))
    
    # Fields
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
    # Foreign Key pointing to PERSON.person_id
    person_id = Column(Integer, ForeignKey('PERSON.person_id', ondelete='CASCADE'))
    
    # Fields
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
    
    # Create DB if it doesn't exist
    engine_server = get_engine(include_db=False)
    with engine_server.connect() as conn:
        print(f"1. Checking for database: {db_name}...")
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
    
    # Create Tables
    engine_db = get_engine(include_db=True)
    print("2. Pushing ORM tables to MySQL...")
    Base.metadata.create_all(engine_db)
    
    print("3. Schema generation complete! (Task_1: 4 tables created only)")
    return engine_db

if __name__ == "__main__":
    setup_schema()