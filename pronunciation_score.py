import librosa
import numpy as np
from dtw import dtw

def extract_mfcc(file):
    y, sr = librosa.load(file, sr=16000)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return mfcc.T

# reference pronunciation
ref_audio = "../LibriSpeech/test-clean/1089/134686/1089-134686-0000.flac"

# patient pronunciation (same file for testing)
patient_audio = "../LibriSpeech/test-clean/1089/134686/1089-134686-0000.flac"

ref = extract_mfcc(ref_audio)
patient = extract_mfcc(patient_audio)

alignment = dtw(ref, patient)
distance = alignment.distance

score = max(0, 100 - distance)

print("Pronunciation Score:", score)