import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Load environment variables (ensure you have a .env file in your Task 3 folder)
load_dotenv()

# Define the connection URL using your existing environment variables
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME  = os.getenv("DB_NAME", "consultbae_db")


SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Create the engine and session factory
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- ORM Models mapping to your EXISTING tables ---

class Person(Base):
    __tablename__ = 'PERSON'

    person_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name_normalized = Column(String(255))
    phone_normalized = Column(String(50), unique=True)
    # We only need the fields relevant to Task 3 to interact with the table
    
    # Relationship to audio submissions
    audio_submissions = relationship("AudioSubmission", back_populates="person")


class AudioSubmission(Base):
    __tablename__ = 'AUDIO_SUBMISSION'

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('PERSON.person_id', ondelete='CASCADE'))
    file_path = Column(String(500))
    duration_sec = Column(Float)
    sample_rate = Column(Integer)
    bitrate_kbps = Column(Integer)
    loudness_db = Column(Float)
    # Note: Removed 'quality' from the previous example to perfectly match your task1 schema

    person = relationship("Person", back_populates="audio_submissions")


# --- Dependency injection for FastAPI ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()