import streamlit as st
from streamlit_option_menu import option_menu

from dashboard.data_loader import load_dashboard_data
from dashboard.methodology import render_methodology
from dashboard.overview import render_overview
from dashboard.representation import render_representation
from dashboard.video_comparison import render_video_comparison




st.set_page_config(
    page_title="Challenge Mujeres IA",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


try:
    aggregate_data, gender_data = (
        load_dashboard_data()
    )

except FileNotFoundError as error:
    st.error(str(error))

    st.code(
        "outputs/\n"
        "├── aggregate_metrics.json\n"
        "└── gender_metrics.json"
    )

    st.stop()


st.sidebar.title(
    "Challenge Mujeres IA"
)

st.sidebar.markdown(
    """
Análisis multimodal de presencia y protagonismo en
conferencias tecnológicas.
"""
)

st.sidebar.divider()

navigation = option_menu(
    menu_title=None,
    options=[
        "Resumen",
        "Comparación por vídeo",
        "Representación",
        "Metodología"
    ],
    icons=[
        "bar-chart",
        "camera-video",
        "people",
        "info-circle"
    ],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "6px",
            "background-color": "#EEEAF7",
            "border-radius": "14px",
            "margin-bottom": "28px"
        },
        "icon": {
            "color": "#6D5B98",
            "font-size": "16px"
        },
        "nav": {
            "justify-content": "space-between"
        },
        "nav-item": {
            "flex-grow": "1"
        },
        "nav-link": {
            "font-size": "15px",
            "font-weight": "500",
            "text-align": "center",
            "margin": "0 3px",
            "padding": "11px 16px",
            "border-radius": "10px",
            "color": "#4A425C",
            "background-color": "transparent"
        },
        "nav-link-selected": {
            "background-color": "#7C3AED",
            "color": "#FFFFFF",
            "font-weight": "650"
        }
    }
)

st.sidebar.divider()

mapping = gender_data[
    "mapping_coverage"
]

st.sidebar.metric(
    "Vídeos",
    len(aggregate_data["videos"])
)

st.sidebar.metric(
    "Clusters de voz",
    mapping["total_speakers"]
)

st.sidebar.metric(
    "Cobertura anotada",
    (
        f"{mapping['verified_speaking_time_percentage']:.1f}%"
    )
)

st.title(
    "🎙️ Presencia y protagonismo en conferencias tecnológicas"
)


if navigation == "Resumen":

    render_overview(
        aggregate_data,
        gender_data
    )


elif navigation == "Comparación por vídeo":

    render_video_comparison(
        aggregate_data
    )


elif navigation == "Representación":

    render_representation(
        gender_data
    )


elif navigation == "Metodología":

    render_methodology()