import os

dataset_path = "../LibriSpeech/test-clean"

data = []

for speaker in os.listdir(dataset_path):
    speaker_path = os.path.join(dataset_path, speaker)

    for chapter in os.listdir(speaker_path):
        chapter_path = os.path.join(speaker_path, chapter)

        for file in os.listdir(chapter_path):
            if file.endswith(".trans.txt"):
                with open(os.path.join(chapter_path, file)) as f:
                    lines = f.readlines()

                    for line in lines:
                        parts = line.strip().split(" ", 1)
                        audio_id = parts[0]
                        text = parts[1]

                        audio_file = audio_id + ".flac"
                        audio_path = os.path.join(chapter_path, audio_file)

                        data.append((audio_path, text))

print("Total samples:", len(data))
print(data[:5])
