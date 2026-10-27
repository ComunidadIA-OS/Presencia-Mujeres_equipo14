import json
from collections import defaultdict
from pathlib import Path

import cv2
from ultralytics import YOLO

import sys

#VIDEO_PATH = "data/raw/V001_sample.webm"
#OUTPUT_PATH = Path("outputs/V001_tracks.json")

if len(sys.argv) <2:
    raise RuntimeError("Uso: python src/audio/person_tracking.py VIDEO_ID")

VIDEO_ID = sys.argv[1]
VIDEO_PATH = Path(f"data/raw/{VIDEO_ID}.webm")
OUTPUT_PATH = Path(f"outputs/{VIDEO_ID}_tracks.json")

MODEL_NAME = "yolo11n.pt"
CONFIDENCE = 0.40

model = YOLO(MODEL_NAME)

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    raise RuntimeError(
        f"No se pudo abrir el vídeo: {VIDEO_PATH}"
    )

fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
video_duration = total_frames / fps

print(f"FPS: {fps:.2f}")
print(f"Total de frames: {total_frames}")
print(f"Duración: {video_duration:.2f} segundos")

# track_id -> lista de detecciones
tracks = defaultdict(list)

frame_idx = 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # IMPORTANTE:
    # ByteTrack recibe todos los frames consecutivos.
    result = model.track(frame, persist=True, classes=[0],        # Clase person
        tracker="bytetrack.yaml",
        conf=CONFIDENCE,
        verbose=False
    )[0]

    if (result.boxes is not None  and result.boxes.id is not None):
        timestamp = frame_idx / fps

        track_ids = (result.boxes.id.int().cpu().tolist())

        boxes = (result.boxes.xyxyn.cpu().tolist())

        confidences = (result.boxes.conf.cpu().tolist())

        for track_id, box, confidence in zip(track_ids,boxes,confidences):
            tracks[track_id].append({
                "t": round(timestamp, 3),
                "bbox": [
                    round(value, 4)
                    for value in box
                ],
                "confidence": round(confidence, 4)
            })

    frame_idx += 1

    # Progreso aproximadamente cada 10 segundos
    if frame_idx % max(1, int(fps * 10)) == 0:
        print(f"{frame_idx / fps:.0f} s procesados | " f"IDs acumulados: {len(tracks)}")

cap.release()

OUTPUT_PATH.parent.mkdir(parents=True,exist_ok=True)

output = []

for track_id, detections in sorted(tracks.items()):
    first_seen = detections[0]["t"]
    last_seen = detections[-1]["t"]

    # Tiempo basado en número de frames detectados.
    screen_time = len(detections) / fps

    output.append({
        "track_id": track_id,
        "first_seen": round(first_seen, 3),
        "last_seen": round(last_seen, 3),
        "screen_time": round(screen_time, 3),
        "detections": detections
    })

OUTPUT_PATH.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")

print("\n=== RESULTADOS DE TRACKING ===")

# Imprimimos primero los tracks con mayor tiempo
sorted_tracks = sorted(tracks.items(),key=lambda item: len(item[1]),reverse=True)

for track_id, detections in sorted_tracks:
    screen_time = len(detections) / fps

    print(f"PERSON_{track_id:03d}: "f"{screen_time:.1f} s en pantalla")

print(f"\nTotal de IDs detectados: {len(tracks)}")
print(f"Resultado guardado en: {OUTPUT_PATH}")