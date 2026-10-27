import json
from pathlib import Path
from faster_whisper import WhisperModel

import sys

#AUDIO_PATH = Path("data/audio/V001_sample.wav")

#OUTPUT_PATH = Path("outputs/V001_transcription.json")

if len(sys.argv) <2:
    raise RuntimeError("Uso: python src/audio/transcription.py VIDEO_ID")

VIDEO_ID = sys.argv[1]
AUDIO_PATH = Path(f"data/audio/{VIDEO_ID}.wav")
OUTPUT_PATH = Path(f"outputs/{VIDEO_ID}_transcription.json")


MODEL_SIZE = "small"
print("Cargando modelo...")

model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

print("transcribiendo audio...")

segments, info = model.transcribe(str(AUDIO_PATH), beam_size=5, vad_filter=True, word_timestamps=True)

print(f"Idioma detectado: {info.language}")
print(f"(probabilidad: {info.language_probability:.2f})")

transcription = []
for segment in segments:

    words = []
    if segment.words:
        for word in segment.words:
            words.append({"start":round(word.start, 3),
                          "end": round(word.end, 3),
                          "word": word.word.strip()})

    transcription.append({
        "start": round(segment.start, 3),
        "end": round(segment.end, 3),
        "duration": round(segment.end -segment.start, 3),
        "text": segment.text.strip(),
        "words":words
    })

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_PATH.open("w", encoding="utf-8") as file:
    json.dump({"language":info.language,
               "language_probability": round(info.language_probability, 4),
               "segments": transcription},
               file, indent=2, ensure_ascii=False)

print(f"\nSegmentos transcritos:" f"{len(transcription)}")

print(f"Resultado guardado en "f"{OUTPUT_PATH}")