from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import librosa
import numpy as np
from dtw import dtw
import soundfile as sf
import os

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DATABASE ----------------
DB_NAME = "speech.db"

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    word TEXT,
    score REAL
)
""")

conn.commit()

# ---------------- ROOT ----------------
@app.get("/")
def home():
    return {"message": "Phono Rehab AI Backend Running"}

# ---------------- SAVE SCORE ----------------
@app.post("/analyze/")
async def analyze_audio(
    username: str = Form(...),
    word: str = Form(...),
    audio: UploadFile = File(...)
):

    # save uploaded file temporarily
    temp_path = f"temp_{audio.filename}"

    with open(temp_path, "wb") as buffer:
        buffer.write(await audio.read())

    # load audio
    y, sr = librosa.load(temp_path)

    # simple pronunciation comparison
    mfcc = librosa.feature.mfcc(y=y, sr=sr)

    # reference (temporary simple baseline)
    ref = np.ones_like(mfcc)

    # DTW distance
    distance = dtw(mfcc.T, ref.T).distance

    # friendly scoring (smooth, non-zero, forgiving)
    score = 100 * np.exp(-distance / 200)
    score = min(100, max(0, score))

    # SAVE TO DATABASE
    cursor.execute(
        "INSERT INTO scores (username, word, score) VALUES (?, ?, ?)",
        (username, word, float(score))
    )

    conn.commit()

    # remove temp file
    os.remove(temp_path)

    return {
        "username": username,
        "word": word,
        "score": round(score, 2)
    }

# ---------------- GET SCORES ----------------
@app.get("/doctor/patients/")
def get_patients():

    cursor.execute("""
        SELECT username, word, score
        FROM scores
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    patients = []

    for row in rows:
        patients.append({
            "username": row[0],
            "word": row[1],
            "score": row[2]
        })

    return patients
# ---------------- PATIENT STATS ----------------
@app.get("/patient/stats/{username}")
def get_patient_stats(username: str):

    cursor.execute("""
        SELECT
            AVG(score),
            COUNT(*),
            MAX(score)
        FROM scores
        WHERE username = ?
    """, (username,))

    result = cursor.fetchone()

    avg_score = result[0] if result[0] is not None else 0
    total_tests = result[1] if result[1] is not None else 0
    best_score = result[2] if result[2] is not None else 0

    return {
        "username": username,
        "average": round(avg_score, 2),
        "tests": total_tests,
        "best": round(best_score, 2)
    }