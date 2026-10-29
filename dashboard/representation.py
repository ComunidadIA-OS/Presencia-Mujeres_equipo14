import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.constants import (
    GENDER_COLORS,
    GENDER_LABELS
)


def render_representation(
    gender_data
):
    st.header(
        "Representación y protagonismo"
    )

    st.info(
        "El género procede de información documentada. "
        "No se infiere mediante imagen, voz, nombre ni "
        "reconocimiento facial."
    )

    global_gender = gender_data["global"]

    st.subheader("Composición de participantes")
    women_count = 9
    men_count = 21
    total_participants = 30

    women_percentage = (women_count/total_participants)*100
    men_percentage = (men_count/total_participants)*100

    col1, col2, col3 = st.columns(3)
    col1.metric("Participantes documentadas como mujeres",
                f"{women_count} de {total_participants}",
                f"{women_percentage:.0f}% del corpus")
    col2.metric("Participantes documentadas como hombres",
                    f"{men_count} de {total_participants}",
                    f"{men_percentage:.0f}% del corpus")

    col3.metric("Participantes totales", total_participants)
    st.caption("El recuento incluye panelistas y voces de la audiencia que fueron anotadas en las cinco muestras.")

    st.divider()
    st.subheader("Tiempo medio hablado por participante:")
    women_speaking_time = global_gender["woman"]["speaking_time_seconds"]
    men_speaking_time = global_gender["man"]["speaking_time_seconds"]
    women_average = (women_speaking_time/women_count)
    men_average = (men_speaking_time/men_count)
    women_average_minutes = (women_average/60)
    men_average_minutes = (men_average/60)

    col1, col2 = st.columns(2)
    col1.metric("Media por participante mujer:", f"{women_average:.0f}s", f"{women_average_minutes:.2f} min")
    col2.metric("Media por participante hombre:", f"{men_average:.0f}s", f"{men_average_minutes:.2f} min")

    st.info("Aunque los hombres acumulan más tiempo de habla total porque son más numerososo, el tiempo medio por participante es mayor entre las mujeres en estas cinco muestras. Aproximadamente 1min 53s frente a 1min 27s. " \
    "Como se ha mencionado, son muestras por lo que no se puede llegar a conclusiones generalistas al respecto.")



    rows = []

    for gender, metrics in (
        global_gender.items()
    ):
        if (
            metrics[
                "speaking_time_seconds"
            ] == 0
            and metrics["turns"] == 0
        ):
            continue

        rows.append({
            "Categoría": GENDER_LABELS.get(
                gender,
                gender
            ),
            "Tiempo de habla (%)":
                metrics[
                    "speaking_percentage"
                ],
            "Turnos":
                metrics["turns"],
            "Aperturas":
                metrics[
                    "opening_count"
                ],
            "Cierres":
                metrics[
                    "closing_count"
                ],
            "Alineación (%)":
                metrics[
                    "visual_alignment_percentage"
                ]
        })

    dataframe = pd.DataFrame(rows)

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True
    )

    left, right = st.columns(2)

    with left:
        figure = px.bar(
            dataframe,
            x="Categoría",
            y="Turnos",
            color="Categoría",
            text_auto=True,
            color_discrete_map=GENDER_COLORS,
            title="Número de turnos"
        )

        figure.update_layout(
            showlegend=False
        )

        st.plotly_chart(
            figure,
            use_container_width=True
        )

    with right:
        figure = px.bar(
            dataframe,
            x="Categoría",
            y="Alineación (%)",
            color="Categoría",
            text_auto=".2f",
            color_discrete_map=GENDER_COLORS,
            title="Alineación voz-imagen"
        )

        figure.update_layout(
            showlegend=False,
            yaxis_range=[0, 100]
        )

        figure.update_traces(
            texttemplate="%{y:.2f}%",
            textposition="outside"
        )

        st.plotly_chart(
            figure,
            use_container_width=True
        )

    st.warning(
        "La alineación voz-imagen no equivale a "
        "presencia visual. V004 y V005 mantienen "
        "varios participantes visibles de forma "
        "simultánea y se conservan como ambiguos."
    )

    st.subheader(
        "Aperturas y cierres"
    )

    opening_rows = []

    for _, row in dataframe.iterrows():
        opening_rows.extend([
            {
                "Categoría": row[
                    "Categoría"
                ],
                "Tipo": "Apertura",
                "Cantidad": row[
                    "Aperturas"
                ]
            },
            {
                "Categoría": row[
                    "Categoría"
                ],
                "Tipo": "Cierre",
                "Cantidad": row[
                    "Cierres"
                ]
            }
        ])

    opening_df = pd.DataFrame(
        opening_rows
    )

    figure = px.bar(
        opening_df,
        x="Categoría",
        y="Cantidad",
        color="Tipo",
        barmode="group",
        text_auto=True,
        color_discrete_map={
            "Apertura": "#8B5CF6",
            "Cierre": "#F59E0B"
        }
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )