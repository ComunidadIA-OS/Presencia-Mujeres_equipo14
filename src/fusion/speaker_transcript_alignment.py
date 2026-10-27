import json
from pathlib import Path

import sys

if len(sys.argv) <2:
    raise RuntimeError("Uso: python src/audio/speaker_transcript_alignment.py VIDEO_ID")

VIDEO_ID = sys.argv[1]

DIARIZATION_PATH = Path(f"outputs/{VIDEO_ID}_diarization.json")

TRANSCRIPTION_PATH = Path(f"outputs/{VIDEO_ID}_transcription.json")

OUTPUT_PATH = Path(f"outputs/{VIDEO_ID}_speaker_transcript.json")



MIN_SEGMENT_DURATION = 0.5

def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"No se encontró: {path}")

    with path.open("r", encoding = "utf-8") as file:
        return json.load(file)

diarization = load_json(DIARIZATION_PATH)
transcription = load_json(TRANSCRIPTION_PATH)

#palabras Whisper
words = []
for segment in transcription["segments"]:
    for word in segment.get("words", []):
        midpoint = (float(word["start"]) + float(word["end"]))/2

        words.append({
            "start": float(word["start"]),
            "end": float(word["end"]),
            "midpoint": midpoint,
            "word":word["word"]
        })

speaker_transcript = []

for speech_segment in diarization:
    speaker = speech_segment["speaker"]
    start = float(speech_segment["start"])
    end = float(speech_segment["end"])
    duration = float(speech_segment["duration"])

    if duration < MIN_SEGMENT_DURATION:
        continue

    segment_words = [word for word in words if start <=word["midpoint"] <= end]

    text = " ".join(word["word"] for word in segment_words)

    speaker_transcript.append({
        "speaker":speaker,
        "start": start,
        "end": end, 
        "duration": duration,
        "text": text, 
        "word_count": len(segment_words)
    })


OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT_PATH.open("w",encoding="utf-8") as file:
    json.dump(speaker_transcript, file, indent=2, ensure_ascii=False)

print("\n=== SPEAKER + TRANSCRIPT ===\n")
for item in speaker_transcript:
    print(f"{item['speaker']}"
          f"[{item['start']:.1f} - "
          f"{item['end']:.1f}]")

    print(item["text"])
    print()

print(f"Segmentos generados:" f"{len(speaker_transcript)}")

print(f"Resultado guardado en:" f"{OUTPUT_PATH}")