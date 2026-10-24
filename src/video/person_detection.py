#from pathlib import Path
import cv2
from ultralytics import YOLO

VIDEO_PATH = "data/raw/V001_sample.webm"

model=YOLO("yolo11n.pt")

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    raise RuntimeError(f"No se pudo abrir el archivo de video: {VIDEO_PATH}")

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"FPS: {fps}")
print(f"Total de frames: {total_frames}")

frame_count = 0
while True:
    ret, frame =cap.read()
    if not ret:
        break

    frame_count += 1

    # para la prueba, 1 frame por segundo:
    if frame_count % int(fps) != 0:
        continue

    results = model(frame, classes=[0], verbose=False)  # 0 = persona
    detected_people = len(results[0].boxes)  # número de personas detectadas en el frame

    timestamp = frame_count / fps

    print(f"{timestamp:.1f}s: {detected_people} personas detectadas")

cap.release()

print("Detección de personas completada.")

