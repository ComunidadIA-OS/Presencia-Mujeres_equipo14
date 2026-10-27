import json
import os 
from pathlib import Path

from openai import OpenAI

import sys

if len(sys.argv) <2:
    raise RuntimeError("Uso: python src/audio/content_analysis.py VIDEO_ID")

VIDEO_ID = sys.argv[1]

TRANSCRIPT_PATH = Path(f"outputs/{VIDEO_ID}_speaker_transcript.json")
OUTPUT_PATH = Path(f"outputs/{VIDEO_ID}_content_analysis.json")

BASE_URL = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1"

MODEL = "mistral@latest"

MAX_SEGMENTS = None
client = OpenAI(base_url=BASE_URL, api_key=os.environ["OVH_AI_ENDPOINTS_ACCESS_TOKEN"])

def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"No se encontró: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

def analyze_content(text):
    prompt = f"""
    You are analysing an intervention from a technical conference panel. Classify the intervention using exactly ONE of these categories:
    - technical_explanation
    - answer
    - question
    - opinion
    - moderation
    - introduction
    - closing
    - organizational
    - other
    Also classify the technical weight as exactly ONE of:
    - low
    - medium
    - high
    technical_explanation: Explains technical concepts, systems, methods, technologies, research or implementation details.
    answer: Directly responds to a question or previous intervention.
    question: Primarly asks a question.
    opinion: Expresses a viewpoint, judgement or personal perspective.
    moderation: Manages the conversation, introduces speakers, gives turns or redirects discussion.
    introduction: Introduces the session, topic or participant. 
    closing: Concludes or sumarises the session.
    organizational: Logistics, timing or event-related information.
    other: Does not clearly fit another category.
    Return ONLY valid JSON usig this structure:

    {{
    "content_type": "category",
    "technical_weight": "low|medium|high"
    }}

    Intervention:
    {text}

"""
    response = client.chat.completions.create(model=MODEL, messages= [{"role": "user",
                                                                       "content": prompt}],temperature=0, max_tokens=100)

    raw_result = (response.choices[0].message.content.strip())

    raw_result = (raw_result.replace("```json", "").replace("```","").strip())

    return json.loads(raw_result)

transcript = load_json(TRANSCRIPT_PATH)

segments_with_text = [segment for segment in transcript if segment.get("text", "").strip()]

print(f"intervenciones con texto:" f"{len(segments_with_text)}")

results = []

segments_to_analyze = (segments_with_text if MAX_SEGMENTS is None else segments_with_text[:MAX_SEGMENTS])
for i, segment in enumerate(segments_to_analyze, start=1):
    speaker = segment["speaker"]
    text = segment["text"]

    print(f"\nAnalizando {i}/" f"{len(segments_to_analyze)}")

    print(f"{speaker}"
          f"[{segment['start']:.1f} - " f"{segment['end']:.1f}]")

    print(f"Texto:{text[:150]}....")
    try:
        analysis = analyze_content(text)

        result = {
            "speaker": speaker,
            "start": segment['start'],
            "end": segment['end'],
            "duration": segment['duration'],
            "text": text,
            "content_type": analysis['content_type'],
            "technical_weight": analysis['technical_weight']
        }

        results.append(result)

        print(f"Tipo: {result['content_type']}")
        print(f"peso técnico: {result['technical_weight']}")

    except Exception as error:
        print(f"Error analizando segmento: {error}")


OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT_PATH.open("w", encoding="utf-8") as file:
    json.dump(results, file, indent=2, ensure_ascii=False)

print(f"\nResultado guardado en:{OUTPUT_PATH}")