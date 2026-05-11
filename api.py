from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import SessionLocal, User, Score
import librosa
import numpy as np
from dtw import dtw
import shutil

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------- USER MODEL ----------------

class UserData(BaseModel):
    username: str
    password: str

# ---------------- AUDIO FUNCTION ----------------

def extract_mfcc(file):

    y, sr = librosa.load(file, sr=16000)

    y = y / np.max(np.abs(y))

    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=13
    )

    return mfcc.T

# ---------------- REGISTER ----------------

@app.post("/register/")
async def register(user: UserData):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        return {
            "message": "User already exists"
        }

    new_user = User(
        username=user.username,
        password=user.password,
        role="patient"
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "Registration successful"
    }

# ---------------- LOGIN ----------------

@app.post("/login/")
async def login(user: UserData):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.username == user.username,
        User.password == user.password
    ).first()

    if existing_user:

        return {
            "message": "Login successful",
            "role": existing_user.role
        }

    return {
        "message": "Invalid username or password"
    }

# ---------------- PRONUNCIATION ANALYSIS ----------------

@app.post("/analyze/")
async def analyze(
    username: str = Form(...),
    word: str = Form(...),
    file: UploadFile = File(...)
):

    with open("temp.wav", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    reference = f"reference_{word}.wav"

    ref = extract_mfcc(reference)

    pat = extract_mfcc("temp.wav")

    alignment = dtw(ref, pat)

    distance = alignment.distance

    normalized_distance = distance / len(ref)

    score = 100 * np.exp(-normalized_distance / 600)

    score = max(0, min(100, score))

    # SAVE SCORE

    db = SessionLocal()

    new_score = Score(
        username=username,
        word=word,
        score=float(score)
    )

    db.add(new_score)

    db.commit()

    return {
        "score": score
    }
# ---------------- DOCTOR DASHBOARD ----------------

@app.get("/doctor/patients/")
async def get_patients():

    db = SessionLocal()

    scores = db.query(Score).all()

    result = []

    for s in scores:

        result.append({
            "username": s.username,
            "word": s.word,
            "score": s.score
        })

    return result