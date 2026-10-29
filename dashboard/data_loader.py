import json
from pathlib import Path

import streamlit as st

OUTPUT_DIR = Path("outputs")

AGGREGATE_PATH = (OUTPUT_DIR/"aggregate_metrics.json")

GENDER_PATH = (OUTPUT_DIR/"gender_metrics.json")

PARTICIPANTS_PATH = Path("config/participants.json")

@st.cache_data
def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo:{path}")

    with path.open("r", encoding = "utf-8") as file:
        return json.load(file)

@st.cache_data
def load_dashboard_data():
    aggregate_data = load_json(AGGREGATE_PATH)
    gender_data = load_json(GENDER_PATH)
    participants_data = load_json(PARTICIPANTS_PATH)

    return aggregate_data, gender_data, participants_data