import json
import sys
from collections import defaultdict
from pathlib import Path


PARTICIPANTS_PATH = Path(
    "config/participants.json"
)

OUTPUT_DIR = Path("outputs")

OUTPUT_PATH = OUTPUT_DIR / "gender_metrics.json"

VALID_GENDERS = {
    "woman",
    "man",
    "another_declared_gender",
    "unknown"
}


if len(sys.argv) < 2:
    raise RuntimeError(
        "Uso: python src/metrics/gender_metrics.py "
        "VIDEO_ID [VIDEO_ID ...]"
    )


VIDEO_IDS = sys.argv[1:]


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


participants = load_json(
    PARTICIPANTS_PATH
)


def empty_gender_metrics():
    return {
        "speaking_time_seconds": 0.0,
        "turns": 0,
        "opening_count": 0,
        "closing_count": 0,
        "weighted_visual_alignment": 0.0,
        "content_duration_seconds": defaultdict(float),
        "technical_weight_duration_seconds": defaultdict(float),
        "mapped_speakers": 0
    }


metrics_by_gender = defaultdict(
    empty_gender_metrics
)

per_video_results = {}

total_speaking_time = 0.0
verified_speaking_time = 0.0

total_speakers = 0
verified_speakers = 0


for video_id in VIDEO_IDS:

    final_metrics_path = OUTPUT_DIR / (
        f"{video_id}_final_metrics.json"
    )

    video_metrics = load_json(
        final_metrics_path
    )

    video_annotations = participants.get(
        video_id,
        {}
    )

    video_gender_metrics = defaultdict(
        empty_gender_metrics
    )

    for speaker_id, speaker_metrics in (
        video_metrics["speakers"].items()
    ):

        total_speakers += 1

        speaking_time = float(
            speaker_metrics[
                "presence"
            ][
                "speaking_time_seconds"
            ]
        )

        total_speaking_time += speaking_time

        annotation = video_annotations.get(
            speaker_id
        )

        verified = bool(
            annotation
            and annotation.get(
                "speaker_mapping_verified",
                False
            )
        )

        if verified:

            gender = annotation.get(
                "declared_gender",
                "unknown"
            )

            if gender not in VALID_GENDERS:
                gender = "unknown"

            verified_speakers += 1
            verified_speaking_time += (
                speaking_time
            )

        else:
            gender = "unknown"

        global_data = metrics_by_gender[
            gender
        ]

        video_data = video_gender_metrics[
            gender
        ]

        for target in [
            global_data,
            video_data
        ]:

            target[
                "speaking_time_seconds"
            ] += speaking_time

            target["turns"] += int(
                speaker_metrics[
                    "turn_control"
                ][
                    "turns"
                ]
            )

            if speaker_metrics[
                "turn_control"
            ][
                "opens_video"
            ]:
                target[
                    "opening_count"
                ] += 1

            if speaker_metrics[
                "turn_control"
            ][
                "closes_video"
            ]:
                target[
                    "closing_count"
                ] += 1

            visual_alignment = float(
                speaker_metrics[
                    "visual"
                ][
                    "alignment_time_percentage"
                ]
            )

            target[
                "weighted_visual_alignment"
            ] += (
                speaking_time
                * visual_alignment
            )

            content_durations = (
                speaker_metrics[
                    "content"
                ][
                    "duration_by_content_type_seconds"
                ]
            )

            for content_type, duration in (
                content_durations.items()
            ):
                target[
                    "content_duration_seconds"
                ][
                    content_type
                ] += float(duration)

            technical_durations = (
                speaker_metrics[
                    "technical_weight"
                ][
                    "duration_seconds"
                ]
            )

            for weight, duration in (
                technical_durations.items()
            ):
                target[
                    "technical_weight_duration_seconds"
                ][
                    weight
                ] += float(duration)

        if verified:
            global_data[
                "mapped_speakers"
            ] += 1

            video_data[
                "mapped_speakers"
            ] += 1

    per_video_results[
        video_id
    ] = video_gender_metrics


def finish_gender_metrics(
    raw_metrics,
    speaking_total
):
    finished = {}

    for gender in [
        "woman",
        "man",
        "another_declared_gender",
        "unknown"
    ]:

        data = raw_metrics[gender]

        speaking_time = data[
            "speaking_time_seconds"
        ]

        speaking_percentage = (
            speaking_time
            / speaking_total
            * 100
            if speaking_total > 0
            else 0.0
        )

        visual_alignment = (
            data[
                "weighted_visual_alignment"
            ]
            / speaking_time
            if speaking_time > 0
            else 0.0
        )

        content_duration = dict(
            data[
                "content_duration_seconds"
            ]
        )

        total_content_duration = sum(
            content_duration.values()
        )

        content_percentage = {
            content_type: round(
                duration
                / total_content_duration
                * 100,
                2
            )
            for content_type, duration
            in content_duration.items()
            if total_content_duration > 0
        }

        technical_duration = {
            "low": float(
                data[
                    "technical_weight_duration_seconds"
                ].get("low", 0.0)
            ),
            "medium": float(
                data[
                    "technical_weight_duration_seconds"
                ].get("medium", 0.0)
            ),
            "high": float(
                data[
                    "technical_weight_duration_seconds"
                ].get("high", 0.0)
            )
        }

        total_technical_duration = sum(
            technical_duration.values()
        )

        technical_percentage = {
            weight: round(
                duration
                / total_technical_duration
                * 100,
                2
            )
            if total_technical_duration > 0
            else 0.0
            for weight, duration
            in technical_duration.items()
        }

        finished[gender] = {
            "speaking_time_seconds": round(
                speaking_time,
                3
            ),
            "speaking_percentage": round(
                speaking_percentage,
                2
            ),
            "turns": data["turns"],
            "opening_count": data[
                "opening_count"
            ],
            "closing_count": data[
                "closing_count"
            ],
            "visual_alignment_percentage": round(
                visual_alignment,
                2
            ),
            "mapped_speakers": data[
                "mapped_speakers"
            ],
            "content_duration_seconds": {
                key: round(value, 3)
                for key, value
                in content_duration.items()
            },
            "content_percentage": (
                content_percentage
            ),
            "technical_weight_duration_seconds": {
                key: round(value, 3)
                for key, value
                in technical_duration.items()
            },
            "technical_weight_percentage": (
                technical_percentage
            )
        }

    return finished


finished_global = finish_gender_metrics(
    metrics_by_gender,
    total_speaking_time
)

finished_per_video = {}

for video_id, raw_metrics in (
    per_video_results.items()
):

    video_speaking_total = sum(
        data[
            "speaking_time_seconds"
        ]
        for data in raw_metrics.values()
    )

    finished_per_video[
        video_id
    ] = finish_gender_metrics(
        raw_metrics,
        video_speaking_total
    )


mapping_coverage_percentage = (
    verified_speaking_time
    / total_speaking_time
    * 100
    if total_speaking_time > 0
    else 0.0
)


output = {
    "videos_analyzed": VIDEO_IDS,
    "mapping_coverage": {
        "total_speakers": total_speakers,
        "verified_speakers": verified_speakers,
        "total_speaking_time_seconds": round(
            total_speaking_time,
            3
        ),
        "verified_speaking_time_seconds": round(
            verified_speaking_time,
            3
        ),
        "verified_speaking_time_percentage": round(
            mapping_coverage_percentage,
            2
        )
    },
    "global": finished_global,
    "videos": finished_per_video,
    "methodology": {
        "gender_inferred": False,
        "speaker_mapping": (
            "manual_audio_video_review"
        ),
        "unverified_mapping_category": (
            "unknown"
        )
    }
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


print()
print("=" * 70)
print("MÉTRICAS AGREGADAS POR GÉNERO")
print("=" * 70)

print(
    f"Vídeos analizados: "
    f"{len(VIDEO_IDS)}"
)

print(
    f"Speakers totales: "
    f"{total_speakers}"
)

print(
    f"Speakers con mapping verificado: "
    f"{verified_speakers}"
)

print(
    f"Cobertura temporal verificada: "
    f"{mapping_coverage_percentage:.2f}%"
)

print()

for gender, metrics in (
    finished_global.items()
):

    print(gender)

    print(
        f"  Tiempo hablado: "
        f"{metrics['speaking_time_seconds']:.2f} s"
    )

    print(
        f"  Porcentaje de habla: "
        f"{metrics['speaking_percentage']:.2f}%"
    )

    print(
        f"  Turnos: "
        f"{metrics['turns']}"
    )

    print(
        f"  Aperturas: "
        f"{metrics['opening_count']}"
    )

    print(
        f"  Cierres: "
        f"{metrics['closing_count']}"
    )

    print(
        f"  Alineación visual: "
        f"{metrics['visual_alignment_percentage']:.2f}%"
    )

    print()


print(
    f"Resultado guardado en: "
    f"{OUTPUT_PATH}"
)