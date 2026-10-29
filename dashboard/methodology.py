import streamlit as st

def render_methodology():
    st.header("Metodología y transparencia")

    st.subheader("Pipeline multimodal")

    st.code("""
    VIDEO
 ├── AUDIO
 │    ├── FFmpeg
 │    ├── pyannote
 │    └── faster-whisper
 │
 ├── IMAGE
 │    ├── YOLO
 │    └── ByteTrack
 │
 ├── FUSION
 │    ├── speaker ↔ transcript
 │    └── speaker ↔ visual prominence
 │
 ├── CONTENT
 │    └── OVHcloud AI Endpoints / Mistral
 │
 └── ANNOTATION
      └── manual speaker-participant mapping

    """)

    left, right = st.columns(2)
    with left:
        st.subheader("Principios éticos")
        st.markdown("""
- Sin reconocimiento facial.
- Sin inferencia de género por imagen.
- Sin inferencia de género por voz.
- Sin inferencia de género por nombre.
- IDs visuales anónimos y temporales.
- Clasificación semántica limitada al texto.
- Asociaciones ambiguas no forzadas
- Resultados agregados


""")

    with right:
        st.subheader("Limitaciones")

        st.markdown("""

- Solo cinco fragmentos analizados.
- Selección no representativa del conjunto de conferencias.
- Posibles errores de diarización.
- Microsegmentos falsos. 
- Fragmentación de tracks por cambios de cámara.
- Preguntas fuera de plano. 
- Planos grupales ambiguos.
- Clasificación semántica dependiente del LLM.
- Mapping speaker-participante manual (check de género).
        """)

    st.divider()

    st.subheader("Tecnologías")

    col1, col2, col3 = st.columns(3)

    col1.markdown("""

**Audio**
- FFmpeg
- pyannote.audio
- faster-whisper
    """)

    col2.markdown("""
**Vídeo**
- OpenCV
- Ultralytics YOLO
- ByteTrack
    """)

    col3.markdown("""
**Contenido y dashboard**
- OVHcloud AI Endpoints
- Mistral
- Streamlit
- Plotly
    """)