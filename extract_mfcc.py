import librosa
import numpy as np

audio_file = "../LibriSpeech/test-clean/1089/134686/1089-134686-0000.flac"

# Load audio
y, sr = librosa.load(audio_file)

# Extract MFCC
mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

print("MFCC shape:", mfcc.shape)
print("MFCC sample values:")
print(mfcc[:, :5])
