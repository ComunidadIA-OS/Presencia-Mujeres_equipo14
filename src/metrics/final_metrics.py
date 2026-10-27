import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

if len(sys.argv) <2:
    raise RuntimeError("Uso: python src/audio/final_metrics.py VIDEO_ID")

VIDEO_ID = sys.argv[1]

PROMINENCE_PATH = Path(f"outputs/{VIDEO_ID}_prominence.json")

CONTENT_PATH = Path(f"outputs/{VIDEO_ID}_content_analysis.json")
OUTPUT_PATH = Path(f"outputs/{VIDEO_ID}_final_metrics.json")

def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"No se encontró: {path}")
    with path.open("r", encoding = "utf-8") as file:
        return json.load(file)

prominence = load_json(PROMINENCE_PATH)
content_analysis = load_json(CONTENT_PATH)

# Agrupar análisis por speaker:
semantic_by_speaker = defaultdict(
    lambda:{ "content_types": Counter(),
           "technical_weights": Counter(),
           "duration_by_content_type": defaultdict(float),
           "duration_by_technical_weight": defaultdict(float),
           "total_segments": 0}
)

for i in content_analysis:
    speaker = i["speaker"]
    content_type = i["content_type"]
    technical_weight = i["technical_weight"]
    duration = float(i["duration"])

    data = semantic_by_speaker[speaker]
    data["content_types"][content_type] +=1
    data["technical_weights"][technical_weight] +=1
    data["duration_by_content_type"][content_type] += duration
    data["duration_by_technical_weight"][technical_weight] +=duration
    data["total_segments"] +=1

# Construir salida

final_speakers = {}
for speaker, metrics in prominence["speakers"].items():
    semantic = semantic_by_speaker[speaker]

    total_semantic_duration = sum(semantic["duration_by_technical_weight"].values())
    technical_weight_time_percentage = {}
    for weight in ["low", "medium", "high"]:
        weight_duration = (semantic["duration_by_technical_weight"].get(weight, 0.0))
        percentage = (weight_duration/total_semantic_duration *100 if total_semantic_duration > 0 else 0.0)

        technical_weight_time_percentage[weight] = round(percentage, 2)

    # tipo de contenido dominante por duración
    if semantic["duration_by_content_type"]:
        dominant_content_type = max(semantic["duration_by_content_type"], key=semantic["duration_by_content_type"].get)

    else:
        dominant_content_type = None

    final_speakers[speaker] = {

        "presence": {
            "speaking_time_seconds":
                metrics["speaking_time"],

            "speaking_percentage":
                metrics["speaking_percentage"]
        },

        "turn_control": {
            "turns":
                metrics["turns"],

            "average_turn_duration_seconds":
                metrics["average_turn_duration"],

            "maximum_turn_duration_seconds":
                metrics["maximum_turn_duration"],

            "opens_video":
                metrics["opens_video"],

            "closes_video":
                metrics["closes_video"]
        },

        "visual": {
            "alignment_time_percentage":
                metrics[
                    "visual_alignment"
                ][
                    "time_rate_percentage"
                ],

            "alignment_segment_percentage":
                metrics[
                    "visual_alignment"
                ][
                    "segment_rate_percentage"
                ],

            "ambiguous_segments":
                metrics[
                    "visual_alignment"
                ][
                    "ambiguous_segments"
                ]
        },

        "content": {
            "segments_analyzed":
                semantic["total_segments"],

            "dominant_content_type":
                dominant_content_type,

            "content_type_counts":
                dict(
                    semantic["content_types"]
                ),

            "duration_by_content_type_seconds": {
                key: round(value, 3)
                for key, value
                in semantic[
                    "duration_by_content_type"
                ].items()
            }
        },

        "technical_weight": {
            "counts":
                dict(
                    semantic[
                        "technical_weights"
                    ]
                ),

            "duration_seconds": {
                key: round(value, 3)
                for key, value
                in semantic[
                    "duration_by_technical_weight"
                ].items()
            },

            "time_percentage":
                technical_weight_time_percentage
        }
    }

# Resumen general del video:
output = {

    "video_id": prominence.get(
        "video_id",
        "V001_sample"
    ),

    "summary": {
        "number_of_speakers":
            prominence["summary"][
                "number_of_speakers"
            ],

        "total_speaking_time_seconds":
            prominence["summary"][
                "total_speaking_time"
            ],

        "opening_speaker":
            prominence["summary"][
                "opening_speaker"
            ],

        "closing_speaker":
            prominence["summary"][
                "closing_speaker"
            ]
    },

    "speakers": final_speakers,

    "methodology": {
        "gender_inferred": False,
        "facial_recognition_used": False,

        "semantic_analysis": {
            "provider":
                "OVHcloud AI Endpoints",

            "virtual_model":
                "mistral@latest",

            "task":
                "content classification"
        }
    }
}

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_PATH.open("w", encoding="utf-8") as file:
    json.dump(output, file, ensure_ascii=False, indent=2)


# Consola:

print("\n=== MÉTRICAS FINALES V001 SAMPLE === \n")

for speaker, metrics in final_speakers.items():
    print(speaker)
    print(f"Habla:" f"{metrics['presence']['speaking_percentage']:.2f}%")

    print(f"Turnos:" f"{metrics['turn_control']['turns']}")

    print(f"  Alineación visual: "f"{metrics['visual']['alignment_time_percentage']:.2f}%")

    print(f"  Contenido dominante: "f"{metrics['content']['dominant_content_type']}")

    technical = metrics["technical_weight"]["time_percentage"]

    print("  Peso técnico por tiempo:")

    print(f"    low:    "f"{technical['low']:.2f}%")

    print( f"    medium: " f"{technical['medium']:.2f}%")

    print(f"    high:   "f"{technical['high']:.2f}%")

    print()


print(f"Resultado guardado en: "f"{OUTPUT_PATH}")