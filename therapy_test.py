import librosa
import numpy as np
from dtw import dtw

def extract_mfcc(file):
    y, sr = librosa.load(file, sr=16000)
    y = y / np.max(np.abs(y))
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return mfcc.T

reference = "reference_pa.wav"
patient = "patient_audio.wav"

ref = extract_mfcc(reference)
pat = extract_mfcc(patient)

alignment = dtw(ref, pat)
distance = alignment.distance

normalized_distance = distance / len(ref)

score = 100 - (normalized_distance / 2)
score = max(0, min(100, score))

print("Reference Word: PA")
print("Patient Audio: Recorded Input")
print("Pronunciation Score:", score)