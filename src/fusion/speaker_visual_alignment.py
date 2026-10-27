import json
from collections import defaultdict
from pathlib import Path

import sys

if len(sys.argv) <2:
    raise RuntimeError("Uso: python src/audio/spaker_visual_alignment.py VIDEO_ID")

VIDEO_ID = sys.argv[1]

DIARIZATION_PATH = Path(f"outputs/{VIDEO_ID}_diarization.json")

TRACKS_PATH =Path(f"outputs/{VIDEO_ID}_tracks.json")

OUTPUT_PATH = Path(f"outputs/{VIDEO_ID}_speaker_visual_alignment.json")


# Filtros configurables.
# Las coordenadas de los bounding boxes están normalizadas entre 0 y 1.
VIDEO_FPS = 25.0

MIN_BOX_AREA = 0.025
MIN_BOX_HEIGHT = 0.20

PROMINENT_AREA = 0.25

# Para aceptar un track como candidato visual.
MIN_VISIBILITY_COVERAGE = 0.20
MIN_DOMINANCE = 0.45
MIN_CONFIDENCE_MARGIN = 0.08
MIN_SEGMENT_DURATION = 0.5


def visual_prominence(bbox):
    metrics = bbox_metrics(bbox)
    normalized_area = min(metrics["area"]/PROMINENT_AREA, 1.0)
    score = (0.70*normalized_area + 0.30*metrics["centrality"])
    metrics["normalized_area"] = normalized_area
    return score, metrics

def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def bbox_metrics(bbox):
    """
    Calcula tamaño, altura y centralidad del bounding box.

    bbox:
        [x1, y1, x2, y2]
        con coordenadas normalizadas.
    """

    x1, y1, x2, y2 = bbox

    width = max(0.0, x2 - x1)
    height = max(0.0, y2 - y1)
    area = width * height

    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    # Distancia respecto al centro de la imagen.
    distance_to_center = ((center_x - 0.5) ** 2+ (center_y - 0.5) ** 2) ** 0.5

    # Cuanto más cerca del centro, mayor valor.
    centrality = max(0.0,1.0 - distance_to_center / 0.7071 )

    return {
        "width": width,
        "height": height,
        "area": area,
        "centrality": centrality
    }


def visual_prominence(bbox):
    """
    Heurística de prominencia visual.

    Damos más peso al tamaño que a la posición central.
    """

    metrics = bbox_metrics(bbox)

    score = (0.75 * metrics["area"]+ 0.25 * metrics["centrality"])

    return score, metrics


diarization = load_json(DIARIZATION_PATH)
tracks_data = load_json(TRACKS_PATH)


# Convertimos la estructura por tracks en una lista de detecciones.
detections = []

for track in tracks_data:
    track_id = track["track_id"]

    for detection in track["detections"]:
        detections.append({
            "track_id": track_id,
            "t": detection["t"],
            "bbox": detection["bbox"],
            "confidence": detection.get(
                "confidence"
            )
        })


# Ordenamos temporalmente para facilitar el análisis.
detections.sort(
    key=lambda item: item["t"]
)


alignment_results = []


for segment in diarization:

    speaker = segment["speaker"]
    start = segment["start"]
    end = segment["end"]
    duration = segment["duration"]

    if duration < MIN_SEGMENT_DURATION:
        alignment_results.append({
            "speaker": speaker,
            "start": start,
            "end": end,
            "duration": duration,
            "candidate_track": None,
            "status": "segment_too_short",
            "confidence_margin": 0.0,
            "candidates": []
        })
        continue

    track_statistics = defaultdict(
        lambda: {
            "detections": 0,
            "prominence_sum": 0.0,
            "area_sum": 0.0,
            "centrality_sum": 0.0,
            "first_seen": None,
            "last_seen": None
        }
    )

    segment_detections = [
        detection
        for detection in detections
        if start <= detection["t"] <= end
    ]

    for detection in segment_detections:

        track_id = detection["track_id"]
        bbox = detection["bbox"]

        prominence, metrics = visual_prominence(
            bbox
        )

        # Descartamos personas demasiado pequeñas.
        # Suelen ser público, imágenes proyectadas
        # o detecciones visualmente poco relevantes.
        if metrics["area"] < MIN_BOX_AREA:
            continue

        if metrics["height"] < MIN_BOX_HEIGHT:
            continue

        stats = track_statistics[track_id]

        stats["detections"] += 1
        stats["prominence_sum"] += prominence
        stats["area_sum"] += metrics["area"]
        stats["centrality_sum"] += metrics[
            "centrality"
        ]

        if stats["first_seen"] is None:
            stats["first_seen"] = detection["t"]

        stats["last_seen"] = detection["t"]


    candidates = []

    total_prominence = sum(
        values["prominence_sum"]
        for values in track_statistics.values()
    )

    for track_id, stats in track_statistics.items():

        detection_count = stats["detections"]

        average_prominence = (
            stats["prominence_sum"]
            / detection_count
        )

        average_area = (
            stats["area_sum"]
            / detection_count
        )

        average_centrality = (
            stats["centrality_sum"]
            / detection_count
        )

        
        visible_duration = (detection_count / VIDEO_FPS)

        visibility_coverage = (
            min(visible_duration / duration, 1.0)
            if duration > 0
            else 0.0
        )

        dominance = (
            stats["prominence_sum"]
            / total_prominence
            if total_prominence > 0
            else 0.0
        )

        # La puntuación combina:
        # - cuánto tiempo aparece durante el segmento;
        # - cuánto domina visualmente.
        alignment_score = (
            0.55 * min(visibility_coverage, 1.0)
            + 0.45 * dominance
        )

        candidates.append({
            "track_id": track_id,
            "detections": detection_count,
            "visible_duration": round(
                visible_duration,
                3
            ),
            "visibility_coverage": round(
                visibility_coverage,
                4
            ),
            "average_area": round(
                average_area,
                4
            ),
            "average_centrality": round(
                average_centrality,
                4
            ),
            "dominance": round(
                dominance,
                4
            ),
            "alignment_score": round(
                alignment_score,
                4
            )
        })


    candidates.sort(
        key=lambda item: item["alignment_score"],
        reverse=True
    )

    selected_track = None
    alignment_status = "no_visual_candidate"
    confidence = 0.0

    if candidates:

        best_candidate = candidates[0]

        if len(candidates) > 1:
            second_score = candidates[1][
                "alignment_score"
            ]

            confidence = max(
                0.0,
                best_candidate["alignment_score"]
                - second_score
            )
        else:
            confidence = best_candidate[
                "alignment_score"
            ]

        enough_coverage = (
            best_candidate["visibility_coverage"]
            >= MIN_VISIBILITY_COVERAGE
        )

        enough_dominance = (
            best_candidate["dominance"]
            >= MIN_DOMINANCE
        )

        enough_margin = (confidence >= MIN_CONFIDENCE_MARGIN)

        if enough_coverage and enough_dominance and enough_margin:
            selected_track = best_candidate["track_id"]

            alignment_status = ("candidate_selected")
        else:
            alignment_status = ("ambiguous_group_shot")



    alignment_results.append({
        "speaker": speaker,
        "start": start,
        "end": end,
        "duration": duration,
        "candidate_track": selected_track,
        "status": alignment_status,
        "confidence_margin": round(
            confidence,
            4
        ),
        "candidates": candidates[:5]
    })


OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

with OUTPUT_PATH.open(
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        alignment_results,
        file,
        indent=2,
        ensure_ascii=False
    )


selected = sum(
    1
    for result in alignment_results
    if result["status"] == "candidate_selected"
)

ambiguous = sum(
    1
    for result in alignment_results
    if result["status"] == "ambiguous_group_shot"
)

without_candidate = sum(
    1
    for result in alignment_results
    if result["status"] == "no_visual_candidate"
)


print("\n=== SPEAKER-VISUAL ALIGNMENT ===\n")

print(
    f"Segmentos de audio analizados: "
    f"{len(alignment_results)}"
)

print(
    f"Candidato visual seleccionado: "
    f"{selected}"
)

print(
    f"Planos ambiguos: {ambiguous}"
)

print(
    f"Sin candidato visual: "
    f"{without_candidate}"
)

print(
    f"\nResultado guardado en: "
    f"{OUTPUT_PATH}"
)