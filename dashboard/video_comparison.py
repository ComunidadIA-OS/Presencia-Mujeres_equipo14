import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.constants import (VIDEO_DESCRIPTIONS)

def render_video_comparison(aggregate_data):
    st.header("Comparación por vídeo:")

    videos = aggregate_data["videos"]
    selected_video = st.selectbox("Selecciona una muestra", options=list(videos.keys()))

    selected_data = videos[selected_video]

    st.caption(VIDEO_DESCRIPTIONS.get(selected_video, ""))
    col1, col2, col3, col4 = (st.columns(4))

    col1.metric("Speakers", selected_data["number_of_speakers"])
    col2.metric("Speaker principal", selected_data["main_speaker"]["speaker"])
    col3.metric("Alineación voz-imagen", (f"{selected_data["average_visual_alignment_percentage"]:.2f}%"))

    st.divider()
    left, right = st.columns(2)
    with left:
        st.subheader("Tiempo de habla por speaker")

        speaking_df = pd.DataFrame([{"Speaker": speaker, "Porcentaje": percentage} for speaker, percentage in selected_data["speaking_distribution"].items()])

        speaking_df = (speaking_df.sort_values("Porcentaje", ascending=True))

        figure = px.bar(speaking_df, x="Porcentaje", y="Speaker", orientation="h", color="Porcentaje", color_continuous_scale="Purples", text_auto=".2f")


        figure.update_traces(texttemplate="%{x:.2f}%")
        figure.update_layout(coloraxis_showscale=False)

        st.plotly_chart(figure, use_container_width=True)

    with right:
        st.subheader("Tipos de contenido")

        content_df = pd.DataFrame([{"Tipo":content_type, "Porcentaje": percentage} for content_type, percentage in selected_data["content_distribution_percentage"].items()])

        content_df = content_df.sort_values("Porcentaje", ascending=False)
        figure = px.bar(content_df, x="Tipo", y= "Porcentaje", color="Tipo", text_auto=".2f")

        figure.update_layout(showlegend=False, xaxis_tickangle=-25)

        figure.update_traces(texttemplate="%{y:.2f}%", textposition="outside")
        st.plotly_chart(figure, use_container_width=True)

    st.subheader("Peso técnico estimado")
    technical_df = pd.DataFrame([{"Peso":weight.capitalize(), "Porcentaje":percentage} for weight, percentage in selected_data["technical_weight_percentage"].items()])

    figure = px.bar(technical_df, x="Peso", y = "Porcentaje", color = "Peso", text_auto=".2f", color_discrete_map={"Low": "#94A3B8", "Medium": "#F59E0B", "High": "#EF4444"})

    figure.update_layout(showlegend=False, yaxis_range=[0,100])
    figure.update_traces(texttemplate="%{y:.2f}%", textposition="outside")

    st.plotly_chart(figure, use_container_width=True)

    alignment = selected_data["average_visual_alignment_percentage"]

    if alignment == 0:
        st.warning("La alineación es 0% porque no hay cambios de plano. No significa ausencia de participación en pantalla.")