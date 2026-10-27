import json
from pathlib import Path

import cv2
import easyocr

VIDEO_PATH = Path("data/raw/V001_sample.webm")
OUTPUT_PATH = Path("outputs/V001_ocr.json")

#ignoramos resultados OCR con confianza baja:
MIN_CONFIDENCE = 0.40

START_SECONDS= 90
END_SECONDS= 96
SAMPLE_SECONDS= 2.0


print("Cargando EasyOCR...")

reader = easyocr.Reader(["en"], gpu=False)

cap = cv2.VideoCapture(str(VIDEO_PATH))

if not cap.isOpened():
    raise RuntimeError(f"No se pudo abrir el vídeo: {VIDEO_PATH}")

fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

duration = total_frames/ fps

print(f"FPS:{fps:.2f}")
print(f"Duration:{duration:.2f}s")

results = []
timestamp = START_SECONDS

while timestamp < min(END_SECONDS, duration):
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp*1000)

    ok, frame = cap.read()

    if not ok:
        timestamp += SAMPLE_SECONDS
        continue

    height, width = frame.shape[:2]

    #Analizamos la mitad inferior
    roi_y = int(height*0.70)

    roi = frame[roi_y:height, 0:width]

    print(f"procesando frame en {timestamp:.1f}s.....")

    detections = reader.readtext(roi, detail=1)

    frame_texts = []
    for bbox, text, confidence in detections:
        if confidence < MIN_CONFIDENCE:
            continue
        cleaned_text = text.strip()

        if not cleaned_text:
            continue
        frame_texts.append({"text": cleaned_text, "confidence": round(float(confidence),4)})

    if frame_texts:
        results.append({"timestamp": round(timestamp, 3), "text": frame_texts})

        print(f"{timestamp:.1f}s ->" + "|".join(item["text"] for item in frame_texts))

    else:
        print (f"{timestamp:.1f}s -> sin texto")

    timestamp += SAMPLE_SECONDS

cap.release()
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_PATH.open("w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=2)