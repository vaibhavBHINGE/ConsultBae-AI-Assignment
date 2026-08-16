from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydub import AudioSegment
import os
import uuid

# Import from your db.py
from db import get_db, Person, AudioSubmission

app = FastAPI()

# Allow frontend on port 5500 to talk to backend on port 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create folder for audio files and serve it so the HTML can play the audio
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# -----------------------------------------
# 1. Handle Uploads & Audio Processing
# -----------------------------------------
@app.post("/api/submit")
async def submit_audio(
    name: str = Form(...),
    phone: str = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Save file locally
    file_extension = audio_file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"static/uploads/{unique_filename}"
    
    with open(file_path, "wb") as f:
        f.write(await audio_file.read())
        
    # 2. Extract Audio Features using pydub
    try:
        audio = AudioSegment.from_file(file_path)
        duration_sec = len(audio) / 1000.0
        sample_rate_khz = audio.frame_rate # Keep as Hz for DB storage
        file_size_bytes = os.path.getsize(file_path)
        bitrate_kbps = (file_size_bytes * 8) / duration_sec / 1000 if duration_sec > 0 else 0
        loudness_db = audio.dBFS
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")

    # 3. Database Insertion Logic (Handling the Foreign Key)
    try:
        # Check if the person already exists by phone number
        person = db.query(Person).filter(Person.phone_normalized == phone).first()
        
        if not person:
            # Create a new person if they don't exist
            person = Person(
                full_name_normalized=name,
                phone_normalized=phone
            )
            db.add(person)
            db.commit()
            db.refresh(person)
            
        # Create the audio submission linked to the person_id
        new_submission = AudioSubmission(
            person_id=person.person_id,
            file_path=f"/{file_path}",
            duration_sec=round(duration_sec, 2),
            sample_rate=int(sample_rate_khz),
            bitrate_kbps=int(bitrate_kbps),
            loudness_db=round(loudness_db, 2)
        )
        
        db.add(new_submission)
        db.commit()
        
        return {"message": "Success", "submission_id": new_submission.id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------
# 2. Fetch Dashboard Data (THIS WAS MISSING)
# -----------------------------------------
@app.get("/api/submissions")
def get_submissions(db: Session = Depends(get_db)):
    # Join AudioSubmission and Person tables to get names and phone numbers
    results = db.query(AudioSubmission, Person).join(Person, AudioSubmission.person_id == Person.person_id).order_by(AudioSubmission.id.desc()).all()
    
    formatted_data = []
    for audio, person in results:
        formatted_data.append({
            "name": person.full_name_normalized,
            "phone": person.phone_normalized,
            "duration": audio.duration_sec,
            "sample_rate": audio.sample_rate,
            "bitrate": audio.bitrate_kbps,
            "loudness": audio.loudness_db,
            "file_path": audio.file_path
        })
    return formatted_data