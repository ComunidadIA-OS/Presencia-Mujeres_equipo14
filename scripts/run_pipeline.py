import os
import subprocess
import sys
from pathlib import Path


# ============================================================
# ARGUMENTOS
# ============================================================

if len(sys.argv) < 2:
    raise RuntimeError(
        "Uso: python scripts/run_pipeline.py VIDEO_ID"
    )

VIDEO_ID = sys.argv[1]


# ============================================================
# RUTAS
# ============================================================

VIDEO_PATH = Path(
    f"data/raw/{VIDEO_ID}.webm"
)

AUDIO_PATH = Path(
    f"data/audio/{VIDEO_ID}.wav"
)

OUTPUT_DIR = Path("outputs")

DIARIZATION_OUTPUT = OUTPUT_DIR / (
    f"{VIDEO_ID}_diarization.json"
)

TRANSCRIPTION_OUTPUT = OUTPUT_DIR / (
    f"{VIDEO_ID}_transcription.json"
)

TRACKING_OUTPUT = OUTPUT_DIR / (
    f"{VIDEO_ID}_tracks.json"
)

VISUAL_ALIGNMENT_OUTPUT = OUTPUT_DIR / (
    f"{VIDEO_ID}_speaker_visual_alignment.json"
)

TRANSCRIPT_ALIGNMENT_OUTPUT = OUTPUT_DIR / (
    f"{VIDEO_ID}_speaker_transcript.json"
)

PROMINENCE_OUTPUT = OUTPUT_DIR / (
    f"{VIDEO_ID}_prominence.json"
)

CONTENT_ANALYSIS_OUTPUT = OUTPUT_DIR / (
    f"{VIDEO_ID}_content_analysis.json"
)

FINAL_METRICS_OUTPUT = OUTPUT_DIR / (
    f"{VIDEO_ID}_final_metrics.json"
)


# ============================================================
# COMPROBACIONES INICIALES
# ============================================================

if not VIDEO_PATH.exists():
    raise FileNotFoundError(
        f"No se encontró el vídeo: {VIDEO_PATH}"
    )

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

AUDIO_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# FUNCIONES
# ============================================================

def run_step(
    name,
    command,
    expected_output=None
):
    """
    Ejecuta un paso del pipeline.

    Si expected_output ya existe, el paso se omite
    para evitar recalcular resultados costosos.
    """

    if (
        expected_output is not None
        and Path(expected_output).exists()
    ):
        print()
        print(
            f"[SKIP] {name}"
        )
        print(
            f"       Ya existe: {expected_output}"
        )
        return

    print()
    print("=" * 60)
    print(f"PASO: {name}")
    print("=" * 60)
    print()

    result = subprocess.run(
        command
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"El paso '{name}' ha fallado."
        )

    if (
        expected_output is not None
        and not Path(expected_output).exists()
    ):
        raise RuntimeError(
            f"El paso '{name}' terminó, "
            f"pero no generó el archivo esperado: "
            f"{expected_output}"
        )


def check_environment_variable(
    variable_name
):
    """
    Comprueba que existe una variable de entorno
    sin mostrar su valor.
    """

    if not os.environ.get(variable_name):
        raise RuntimeError(
            f"Falta la variable de entorno: "
            f"{variable_name}"
        )


# ============================================================
# INFORMACIÓN DEL PIPELINE
# ============================================================

print()
print("=" * 60)
print("PIPELINE MULTIMODAL")
print("=" * 60)

print(f"Video ID: {VIDEO_ID}")
print(f"Vídeo:    {VIDEO_PATH}")

print()


# ============================================================
# 1. EXTRAER AUDIO
# ============================================================

if AUDIO_PATH.exists():

    print(
        f"[SKIP] Extracción de audio"
    )

    print(
        f"       Ya existe: {AUDIO_PATH}"
    )

else:

    run_step(
        "Extracción de audio",
        [
            "ffmpeg",
            "-y",
            "-i",
            str(VIDEO_PATH),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            str(AUDIO_PATH)
        ],
        AUDIO_PATH
    )


# ============================================================
# 2. DIARIZACIÓN
# ============================================================

if not DIARIZATION_OUTPUT.exists():

    check_environment_variable(
        "HF_TOKEN"
    )

run_step(
    "Diarización",
    [
        sys.executable,
        "src/audio/diarization.py",
        VIDEO_ID
    ],
    DIARIZATION_OUTPUT
)


# ============================================================
# 3. TRANSCRIPCIÓN
# ============================================================

run_step(
    "Transcripción",
    [
        sys.executable,
        "src/audio/transcription.py",
        VIDEO_ID
    ],
    TRANSCRIPTION_OUTPUT
)


# ============================================================
# 4. TRACKING VISUAL
# ============================================================

run_step(
    "Tracking de personas",
    [
        sys.executable,
        "src/video/person_tracking.py",
        VIDEO_ID
    ],
    TRACKING_OUTPUT
)


# ============================================================
# 5. ALINEACIÓN VOZ - IMAGEN
# ============================================================

run_step(
    "Alineación voz-imagen",
    [
        sys.executable,
        "src/fusion/speaker_visual_alignment.py",
        VIDEO_ID
    ],
    VISUAL_ALIGNMENT_OUTPUT
)


# ============================================================
# 6. ALINEACIÓN SPEAKER - TRANSCRIPCIÓN
# ============================================================

run_step(
    "Alineación speaker-transcripción",
    [
        sys.executable,
        "src/fusion/speaker_transcript_alignment.py",
        VIDEO_ID
    ],
    TRANSCRIPT_ALIGNMENT_OUTPUT
)


# ============================================================
# 7. MÉTRICAS DE PROTAGONISMO
# ============================================================

run_step(
    "Métricas de protagonismo",
    [
        sys.executable,
        "src/metrics/prominence.py",
        VIDEO_ID
    ],
    PROMINENCE_OUTPUT
)


# ============================================================
# 8. ANÁLISIS SEMÁNTICO CON OVH
# ============================================================

if not CONTENT_ANALYSIS_OUTPUT.exists():

    check_environment_variable(
        "OVH_AI_ENDPOINTS_ACCESS_TOKEN"
    )

run_step(
    "Análisis semántico",
    [
        sys.executable,
        "src/semantic/content_analysis.py",
        VIDEO_ID
    ],
    CONTENT_ANALYSIS_OUTPUT
)


# ============================================================
# 9. MÉTRICAS FINALES
# ============================================================

run_step(
    "Métricas finales",
    [
        sys.executable,
        "src/metrics/final_metrics.py",
        VIDEO_ID
    ],
    FINAL_METRICS_OUTPUT
)


# ============================================================
# FIN
# ============================================================

print()
print("=" * 60)
print("PIPELINE COMPLETADO")
print("=" * 60)

print()
print(
    f"Resultado final:"
)

print(
    FINAL_METRICS_OUTPUT
)