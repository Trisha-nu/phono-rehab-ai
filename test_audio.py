import librosa

audio_file = "../LibriSpeech/test-clean/1089/134686/1089-134686-0000.flac"

y, sr = librosa.load(audio_file)

print("Audio loaded successfully")
print("Duration:", len(y)/sr, "seconds")
