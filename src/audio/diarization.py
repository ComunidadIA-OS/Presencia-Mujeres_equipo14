import os
import json
from pathlib import Path

import soundfile as sf
import torch
from pyannote.audio import Pipeline

AUDIO_PATH = Path("./data/audio/V001_sample.wav")
OUTPUT_PATH = Path("./data/output/V001_sample_diarization.json")

token = os.environ.get("HF_TOKEN")
if not token:
    raise ValueError("Falta la variable de entorno HF_TOKEN.")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

print("Cargando modelo de diarización...")
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-community-1", token=token)
if torch.cuda.is_available():
    pipeline.to(torch.device("cuda"))

print("Leyendo audio...")
data, sample_rate = sf.read(str(AUDIO_PATH), dtype="float32", always_2d=True)
waveform = torch.from_numpy(data.T).mean(dim=0, keepdim=True)  # mono, forma (1, tiempo)

print("Procesando archivo de audio...")
output = pipeline({"waveform": waveform, "sample_rate": sample_rate})

segments = [
    {
        "start": round(turn.start, 3),
        "end": round(turn.end, 3),
        "speaker": speaker,
        "duration": round(turn.end - turn.start, 3),
    }
    for turn, speaker in output.speaker_diarization
]

OUTPUT_PATH.write_text(json.dumps(segments, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Diarización terminada: {OUTPUT_PATH}  ({len(segments)} segmentos)")