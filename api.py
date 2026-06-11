from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import librosa
import numpy as np
from dtw import dtw
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

# ---------------- ANALYZE AUDIO ----------------

@app.post("/analyze/")
async def analyze_audio(
    username: str = Form(...),
    word: str = Form(...),
    audio: UploadFile = File(...)
):

    try:

        # Save uploaded audio
        temp_path = f"temp_{audio.filename}"

        with open(temp_path, "wb") as buffer:
            buffer.write(await audio.read())

        # Load patient audio
        patient_audio, sr = librosa.load(temp_path, sr=16000)

        patient_mfcc = librosa.feature.mfcc(
            y=patient_audio,
            sr=sr,
            n_mfcc=13
        )

        # Reference file
        ref_path = f"reference_{word.strip().lower()}.wav"

        print("Requested word:", word)
        print("Looking for:", ref_path)
        print("Exists:", os.path.exists(ref_path))

        if not os.path.exists(ref_path):

            if os.path.exists(temp_path):
                os.remove(temp_path)

            return {
                "username": username,
                "word": word,
                "score": 0,
                "error": f"Reference file not found: {ref_path}"
            }

        # Load reference audio
        ref_audio, ref_sr = librosa.load(ref_path, sr=16000)

        ref_mfcc = librosa.feature.mfcc(
            y=ref_audio,
            sr=ref_sr,
            n_mfcc=13
        )

        # DTW comparison
        try:

            alignment = dtw(patient_mfcc.T, ref_mfcc.T)

            if hasattr(alignment, "distance"):
                distance = alignment.distance
            else:
                distance = np.linalg.norm(
                    np.mean(patient_mfcc, axis=1)
                    - np.mean(ref_mfcc, axis=1)
                )

        except Exception as e:

            print("DTW Error:", e)

            distance = np.linalg.norm(
                np.mean(patient_mfcc, axis=1)
                - np.mean(ref_mfcc, axis=1)
            )

        print("Distance =", distance)

        # Better scoring
        normalized_distance = distance / len(ref_mfcc.T)

        score = 100 - normalized_distance

        score = max(0, min(100, score))

        print("Normalized Distance =", normalized_distance)
        print("Final Score =", score)

        # Save score
        cursor.execute(
            """
            INSERT INTO scores(username, word, score)
            VALUES (?, ?, ?)
            """,
            (username, word, float(score))
        )

        conn.commit()

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return {
            "username": username,
            "word": word,
            "score": round(score, 2)
        }

    except Exception as e:

        print("Analyze Error:", str(e))

        return {
            "username": username,
            "word": word,
            "score": 0,
            "error": str(e)
        }

# ---------------- DOCTOR VIEW ----------------

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