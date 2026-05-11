from gtts import gTTS
import os

# Words for dataset
bilabial_sounds = [
    "pa","ba","ma","pap","bab","mam","papa","baba","mama"
]

therapy_words = [
    "ball","bat","book","baby","boy",
    "pen","paper","pet","pig",
    "bus","bag","bed",
    "milk","man","moon","mother","map",
    "cat","dog","sun","cup","fish","leaf",
    "table","doctor","water","window","yellow",
    "flower","banana","tomato","pencil","teacher","hospital"
]

# Folder paths
bilabial_folder = "therapy_dataset/bilabial"
words_folder = "therapy_dataset/words"

os.makedirs(bilabial_folder, exist_ok=True)
os.makedirs(words_folder, exist_ok=True)

# Generate bilabial sounds
for word in bilabial_sounds:
    tts = gTTS(text=word, lang='en')
    filename = f"{bilabial_folder}/{word}.wav"
    tts.save(filename)
    print(f"Created {filename}")

# Generate therapy words
for word in therapy_words:
    tts = gTTS(text=word, lang='en')
    filename = f"{words_folder}/{word}.wav"
    tts.save(filename)
    print(f"Created {filename}")

print("Dataset generation completed!")
