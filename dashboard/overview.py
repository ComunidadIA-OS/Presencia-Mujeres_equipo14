import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.constants import (GENDER_COLORS, GENDER_LABELS)

def format_duration(seconds):
    seconds = float(seconds)

    minutes = int(seconds // 60)
    remaining_seconds = int(
        round(seconds % 60)
    )

    if remaining_seconds == 60:
        minutes += 1
        remaining_seconds = 0

    return (
        f"{minutes} min "
        f"{remaining_seconds:02d} s"
    )


def render_overview(
    aggregate_data,
    gender_data
):
    st.header("Resumen del MVP")

    global_gender = gender_data["global"]

    mapping = gender_data[
        "mapping_coverage"
    ]

    videos = aggregate_data["videos"]

    total_turns = sum(
        metrics["turns"]
        for metrics in global_gender.values()
    )

    total_openings = sum(
        metrics["opening_count"]
        for metrics in global_gender.values()
    )

    total_closings = sum(
        metrics["closing_count"]
        for metrics in global_gender.values()
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Vídeos analizados",
        len(videos)
    )

    col2.metric(
        "Clusters de voz",
        mapping["total_speakers"]
    )

    col3.metric(
        "Tiempo de habla",
        format_duration(
            mapping[
                "total_speaking_time_seconds"
            ]
        )
    )

    col4.metric(
        "Cobertura anotada",
        (
            f"{mapping['verified_speaking_time_percentage']:.1f}%"
        )
    )

    st.divider()

    left, right = st.columns(
        [1.5, 1]
    )

    with left:
        st.subheader(
            "Distribución del tiempo de habla"
        )

        rows = []

        for gender, metrics in (
            global_gender.items()
        ):
            percentage = metrics[
                "speaking_percentage"
            ]

            if percentage <= 0:
                continue

            rows.append({
                "Categoría": (
                    GENDER_LABELS.get(
                        gender,
                        gender
                    )
                ),
                "Porcentaje": percentage
            })

        speaking_df = pd.DataFrame(rows)

        figure = px.bar(
            speaking_df,
            x="Categoría",
            y="Porcentaje",
            color="Categoría",
            text_auto=".2f",
            color_discrete_map=GENDER_COLORS,
            labels={
                "Porcentaje": "Tiempo de habla (%)"
            }
        )

        figure.update_traces(
            texttemplate="%{y:.2f}%",
            textposition="outside"
        )

        figure.update_layout(
            showlegend=False,
            yaxis_range=[0, 100]
        )

        st.plotly_chart(
            figure,
            use_container_width=True
        )

    with right:
        st.subheader(
            "Indicadores de protagonismo"
        )

        st.metric(
            "Turnos",
            total_turns
        )

        st.metric(
            "Aperturas",
            total_openings
        )

        st.metric(
            "Cierres",
            total_closings
        )

    woman_percentage = global_gender[
        "woman"
    ][
        "speaking_percentage"
    ]

    man_percentage = global_gender[
        "man"
    ][
        "speaking_percentage"
    ]

    st.info(
        "En los cinco fragmentos seleccionados para "
        "el MVP, las intervenciones asociadas a "
        "participantes documentadas como mujeres "
        f"representan el {woman_percentage:.2f}% "
        "del tiempo de habla, frente al "
        f"{man_percentage:.2f}% asociado a "
        "participantes documentados como hombres."
    )

    st.caption(
        "Los resultados corresponden únicamente a "
        "los cinco fragmentos seleccionados. No son "
        "generalizables a todas las conferencias."
    )