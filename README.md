# Challenge Mujeres IA: análisis multimodal de conferencias técnicas

Este proyecto desarrolla un sistema abierto para analizar vídeos de conferencias técnicas y cuantificar la presencia y el protagonismo de las personas participantes.

El sistema combina procesamiento de audio, análisis de vídeo y transcripción para medir aspectos como:

- tiempo de habla;
- porcentaje de participación;
- número y duración de turnos;
- apertura y cierre de la conversación;
- prominencia visual;
- alineación entre la voz activa y la persona destacada en pantalla;
- contenido pronunciado por cada hablante.

El género no se infiere a partir de imágenes, voz o apariencia. En fases posteriores solo se incorporará información de género declarada explícitamente y procedente de fuentes verificables.

---

## Estado actual

Actualmente se ha implementado una prueba de concepto sobre un fragmento de aproximadamente ocho minutos de un panel técnico.

El pipeline incluye:

- extracción de audio con FFmpeg;
- diarización de hablantes con pyannote;
- transcripción con faster-whisper;
- detección de personas con YOLO;
- tracking temporal con ByteTrack;
- alineación entre segmentos de voz y candidatos visuales;
- alineación entre hablantes y transcripción;
- métricas preliminares de presencia y protagonismo.

Todavía no se ha implementado:

- OCR de nombres y roles;
- asociación global de tracklets con participantes;
- incorporación de género declarado;
- análisis semántico mediante OVH AI Endpoints;
- índice compuesto final;
- ejecución sobre el conjunto objetivo de 5 a 15 vídeos.

---

## Pipeline

```text
                          VÍDEO
                             │
                  ┌──────────┴──────────┐
                  │                     │
                AUDIO                 IMAGEN
                  │                     │
              FFmpeg                  YOLO
                  │                     │
                  ▼                     ▼
             diarización           detecciones
             con pyannote               │
                  │                 ByteTrack
                  ▼                     │
          SPEAKER_00, 01...             ▼
                  │                tracklets
                  │                     │
                  └──────────┬──────────┘
                             ▼
                  alineación voz-imagen
                             │
                             ▼
                  métricas de presencia
                    y protagonismo

              faster-whisper
                     │
                     ▼
                 transcripción
                     │
                     ▼
          alineación speaker-transcript
