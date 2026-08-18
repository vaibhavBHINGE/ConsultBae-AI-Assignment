# ConsultBae-AI-Assignment
Its an assignment for AI Automation Analyst / Developer at ConsultBee which includes 5 tasks 


## Task 1:

## Overview
This pipeline extracts raw, messy candidate data from three disparate CSV sources (Naukri, Gig Workers, and CBNexus), normalizes the fields, and executes a cascading matching logic to resolve duplicate entities. The final output is a pristine set of unique "Golden Records" stored in a relational MySQL database.

## Project Structure
*   **`normalize.py`**: Contains pure functions for data cleaning (phone normalization, standardizing names/cities, handling shifted CSV rows, and fixing mixed CTC formats).
*   **`match.py`**: The Entity Resolution engine. It merges records across the three sources based on primary keys (Email and Phone) and tracks data lineage (`merged_sources`).
*   **`db.py`**: SQLAlchemy ORM definitions for the database schema. Ensures referential integrity between the Hub table (`PERSON`) and the child source tables.
*   **`ingest.py`**: The main orchestrator script. It extracts the raw data, applies the cleaning and matching logic, and loads the final Golden Records into MySQL.
*   **`.env`**: (Ignored in Git) Stores local MySQL credentials.

## Prerequisites
*   Python 3.8+
*   MySQL Server (running locally)

## Setup & Installation

**1. Install Dependencies**
```bash
pip install -r requirements.txt

# Task 3 - Mini Audio Collection App

This is a web application built for the ConsultBae AI Automation Assignment. It allows gig workers to submit audio recordings (via file upload or browser microphone), automatically extracts audio properties (duration, sample rate, bitrate, loudness), and saves the records to a MySQL database.

## 🛠️ Tech Stack
* **Backend:** FastAPI (Python)
* **Frontend:** Vanilla HTML, CSS, JavaScript (MediaRecorder API)
* **Database:** MySQL via SQLAlchemy ORM
* **Audio Processing:** `pydub`, `numpy`, and `FFmpeg`

---

## ⚙️ Prerequisites

Before running this app, ensure you have the following installed on your system:
1. **Python 3.10+** (Tested on Python 3.13/3.14)
2. **MySQL Server** (Running locally on port 3306)
3. **FFmpeg** (Required by `pydub` to process audio files)
   * **Windows:** Open PowerShell and run: `winget install Gyan.FFmpeg`
   * **Mac:** `brew install ffmpeg`
   * **Linux:** `sudo apt install ffmpeg`

---

## 🚀 Setup & Installation Instructions

### 1. Clone the repository and navigate to the Task 3 folder
\`\`\`bash
cd Task_3/Backend
\`\`\`

### 2. Set up the Python Virtual Environment
\`\`\`bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate
\`\`\`

### 3. Install Python Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Database Setup
Ensure your MySQL server is running. Create a `.env` file in the same folder as `main.py` with your database credentials:
\`\`\`env
DB_USER=root
DB_PASS=your_password_here
DB_HOST=localhost
DB_NAME=consultbae_db
\`\`\`

### 5. Run the Application
Start the FastAPI backend using Uvicorn:
\`\`\`bash
uvicorn main:app --reload
\`\`\`

Open your browser and navigate to: **http://127.0.0.1:8000**

---

## 📖 How to Use the App
1. **Submit Audio:** Fill in your Name and Phone Number. Either click "Choose File" to upload an existing audio file, or click "Start Recording" to record directly from your microphone. Click "Submit Task".
2. **View Dashboard:** Scroll down to the "Submissions Dashboard" to view a list of all audio files. The app will display the extracted properties (Duration, Sample Rate, Bitrate, Loudness) and provide an in-browser audio player.

---