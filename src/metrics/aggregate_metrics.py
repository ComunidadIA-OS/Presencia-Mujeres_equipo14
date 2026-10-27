import json
import sys
from pathlib import Path


OUTPUT_DIR = Path("outputs")


if len(sys.argv) < 2:
    raise RuntimeError(
        "Uso: python src/metrics/aggregate_metrics.py "
        "VIDEO_ID [VIDEO_ID ...]"
    )


VIDEO_IDS = sys.argv[1:]

OUTPUT_PATH = OUTPUT_DIR / "aggregate_metrics.json"


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# ============================================================
# CARGAR TODOS LOS VÍDEOS
# ============================================================

videos = {}

for video_id in VIDEO_IDS:

    path = OUTPUT_DIR / (
        f"{video_id}_final_metrics.json"
    )

    data = load_json(path)

    videos[video_id] = data


# ============================================================
# ANALIZAR CADA VÍDEO
# ============================================================

video_summaries = {}


for video_id, data in videos.items():

    speakers = data["speakers"]

    if not speakers:
        continue

    # ---------------------------------------------
    # Speaker con mayor tiempo de habla
    # ---------------------------------------------

    main_speaker = max(
        speakers,
        key=lambda speaker:
            speakers[speaker][
                "presence"
            ][
                "speaking_percentage"
            ]
    )

    # ---------------------------------------------
    # Distribución del tiempo de habla
    # ---------------------------------------------

    speaking_distribution = {
        speaker: metrics[
            "presence"
        ][
            "speaking_percentage"
        ]
        for speaker, metrics
        in speakers.items()
    }

    # ---------------------------------------------
    # Tipos de contenido agregados por duración
    # ---------------------------------------------

    content_duration = {}

    for speaker_metrics in speakers.values():

        speaker_content = (
            speaker_metrics[
                "content"
            ][
                "duration_by_content_type_seconds"
            ]
        )

        for content_type, duration in (
            speaker_content.items()
        ):

            content_duration[
                content_type
            ] = (
                content_duration.get(
                    content_type,
                    0.0
                )
                + duration
            )

    total_content_duration = sum(
        content_duration.values()
    )

    content_percentage = {}

    for content_type, duration in (
        content_duration.items()
    ):

        percentage = (
            duration
            / total_content_duration
            * 100
            if total_content_duration > 0
            else 0.0
        )

        content_percentage[
            content_type
        ] = round(percentage, 2)


    # ---------------------------------------------
    # Peso técnico agregado por duración
    # ---------------------------------------------

    technical_duration = {
        "low": 0.0,
        "medium": 0.0,
        "high": 0.0
    }

    for speaker_metrics in speakers.values():

        weights = speaker_metrics[
            "technical_weight"
        ][
            "duration_seconds"
        ]

        for weight in technical_duration:

            technical_duration[
                weight
            ] += weights.get(
                weight,
                0.0
            )

    total_technical_duration = sum(
        technical_duration.values()
    )

    technical_percentage = {}

    for weight, duration in (
        technical_duration.items()
    ):

        percentage = (
            duration
            / total_technical_duration
            * 100
            if total_technical_duration > 0
            else 0.0
        )

        technical_percentage[
            weight
        ] = round(
            percentage,
            2
        )


    # ---------------------------------------------
    # Alineación visual media ponderada
    # ---------------------------------------------

    total_speaking_time = 0.0
    weighted_alignment = 0.0

    for speaker_metrics in speakers.values():

        speaking_time = speaker_metrics[
            "presence"
        ][
            "speaking_time_seconds"
        ]

        alignment = speaker_metrics[
            "visual"
        ][
            "alignment_time_percentage"
        ]

        weighted_alignment += (
            speaking_time * alignment
        )

        total_speaking_time += (
            speaking_time
        )

    average_visual_alignment = (
        weighted_alignment
        / total_speaking_time
        if total_speaking_time > 0
        else 0.0
    )


    # ---------------------------------------------
    # Construir resumen
    # ---------------------------------------------

    video_summaries[video_id] = {

        "number_of_speakers":
            data["summary"][
                "number_of_speakers"
            ],

        "total_speaking_time_seconds":
            data["summary"][
                "total_speaking_time_seconds"
            ],

        "opening_speaker":
            data["summary"][
                "opening_speaker"
            ],

        "closing_speaker":
            data["summary"][
                "closing_speaker"
            ],

        "main_speaker": {
            "speaker": main_speaker,

            "speaking_percentage":
                speakers[
                    main_speaker
                ][
                    "presence"
                ][
                    "speaking_percentage"
                ]
        },

        "speaking_distribution":
            speaking_distribution,

        "average_visual_alignment_percentage":
            round(
                average_visual_alignment,
                2
            ),

        "content_distribution_percentage":
            content_percentage,

        "technical_weight_percentage":
            technical_percentage
    }


# ============================================================
# RESULTADO GLOBAL
# ============================================================

output = {

    "videos_analyzed": len(
        video_summaries
    ),

    "video_ids": list(
        video_summaries.keys()
    ),

    "videos": video_summaries
}


OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


with OUTPUT_PATH.open(
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        output,
        file,
        ensure_ascii=False,
        indent=2
    )


# ============================================================
# CONSOLA
# ============================================================

print()
print("=" * 70)
print("COMPARACIÓN DE VÍDEOS")
print("=" * 70)


for video_id, summary in (
    video_summaries.items()
):

    print()
    print(video_id)
    print("-" * len(video_id))

    print(
        f"Speakers: "
        f"{summary['number_of_speakers']}"
    )

    print(
        f"Speaker principal: "
        f"{summary['main_speaker']['speaker']} "
        f"("
        f"{summary['main_speaker']['speaking_percentage']:.2f}%"
        f")"
    )

    print(
        f"Alineación visual media: "
        f"{summary['average_visual_alignment_percentage']:.2f}%"
    )

    print(
        "Peso técnico:"
    )

    weights = summary[
        "technical_weight_percentage"
    ]

    print(
        f"  low:    "
        f"{weights['low']:.2f}%"
    )

    print(
        f"  medium: "
        f"{weights['medium']:.2f}%"
    )

    print(
        f"  high:   "
        f"{weights['high']:.2f}%"
    )

    print(
        "Tipos de contenido:"
    )

    for content_type, percentage in (
        sorted(
            summary[
                "content_distribution_percentage"
            ].items(),
            key=lambda item: item[1],
            reverse=True
        )
    ):

        print(
            f"  {content_type}: "
            f"{percentage:.2f}%"
        )


print()
print(
    f"Resultado agregado guardado en: "
    f"{OUTPUT_PATH}"
)