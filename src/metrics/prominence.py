import json
from collections import defaultdict
from pathlib import Path

import sys
if len(sys.argv) <2:
    raise RuntimeError("Uso: python src/audio/prominence.py VIDEO_ID")

VIDEO_ID = sys.argv[1]

DIARIZATION_PATH = Path(f"data/output/{VIDEO_ID}_diarization.json")
ALIGNMENT_PATH = Path(f"outputs/{VIDEO_ID}_speaker_visual_alignment.json")

OUTPUT_PATH = Path(f"outputs/{VIDEO_ID}_prominence.json")

MIN_SEGMENT_DURATION = 0.5  # segundos
MAX_TURN_GAP = 1.0
ALIGNED_STATUS="candidate_selected"

def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

def merge_speaker_segments(segments):
    """
    Fusiona segmentos consecutivos del mismo speaker cuando la separación temporal es suficientemente pequeña.
    Ejemplo:
    speaker_01 -> 10.0 -15.0
    speaker_01 -> 15.4 -20.0
    como la pausa es pequeña, se convierte en:
    speaker_01 -> 10.0 -20.0
    """
    if not segments:
        return []
    ordered_segments = sorted(segments, key=lambda item: (item["start"], item["end"]))

    merged_turns = []
    for segment in ordered_segments:
        current_turn = { "speaker": segment["speaker"],
                        "start": float(segment["start"]),
                        "end": float(segment["end"])}

        current_turn["duration"] = current_turn["end"] -current_turn["start"]

        if not merged_turns:
            merged_turns.append(current_turn)
            continue
        previous_turn = merged_turns[-1]

        gap = (current_turn["start"] - previous_turn["end"])

        same_speaker = (current_turn["speaker"]== previous_turn["speaker"])
        close_enough = (gap <=MAX_TURN_GAP)

        if same_speaker and close_enough:
            previous_turn["end"]= max(previous_turn["end"], current_turn["end"])

            previous_turn["duration"] = (previous_turn["end"] - previous_turn["start"])

        else:
            merged_turns.append(current_turn)

    return merged_turns

def calculate_alignment_statistics(alignment_results):
    """
    Calcula para cada speaker:
    - duración total evaluada;
    - duración con candidato visual;
    - segmentos evaluados;
    - segmentos alineados.
    """
    statistics = defaultdict(
        lambda: {
            "evaluated_duration": 0.0,
            "aligned_duration": 0.0,
            "evaluated_segments": 0,
            "aligned_segments": 0,
            "ambiguous_segments": 0,
            "no_visual_segments": 0,
            "short_segments": 0,
        }
    )

    for result in alignment_results:
        speaker = result["speaker"]
        duration = float(result["duration"])
        status = result["status"]

        if status == "segment_too_short":

            statistics[speaker][
                "short_segments"
            ] += 1
            continue

        statistics[speaker][
            "evaluated_duration"
        ] += duration

        statistics[speaker][
            "evaluated_segments"
        ] += 1

        if status == ALIGNED_STATUS:
            statistics[speaker][
                "aligned_duration"
            ] += duration

            statistics[speaker][
                "aligned_segments"
            ] += 1

        elif status == "ambiguous_group_shot":
            statistics[speaker][
                "ambiguous_segments"
            ] += 1

        elif status == "no_visual_candidate":
            statistics[speaker][
                "no_visual_segments"
            ] += 1


    return statistics

diarization = load_json(
	DIARIZATION_PATH
)
alignment_results = load_json(
	ALIGNMENT_PATH
)
# Eliminamos únicamente los microsegmentos para las
# métricas derivadas. El JSON original se conserva intacto.
valid_segments = [
	segment
	for segment in diarization
	if float(segment["duration"])
	>= MIN_SEGMENT_DURATION
]
if not valid_segments:
	raise RuntimeError(
    	"No hay segmentos válidos después de aplicar "
    	"el filtro de duración."
	)
turns = merge_speaker_segments(
	valid_segments
)
alignment_statistics = (
	calculate_alignment_statistics(
    	alignment_results
	)
)
# Tiempo real hablado a partir de los segmentos filtrados.
# No utilizamos aquí la duración de los turnos fusionados,
# porque una pausa entre dos segmentos no debe contarse
# como tiempo de habla.
speaking_time = defaultdict(float)
raw_segment_count = defaultdict(int)
for segment in valid_segments:
	speaker = segment["speaker"]
	speaking_time[speaker] += float(
    	segment["duration"]
	)
	raw_segment_count[speaker] += 1
turns_by_speaker = defaultdict(list)
for turn in turns:
	turns_by_speaker[
    	turn["speaker"]
	].append(turn)
total_speaking_time = sum(
	speaking_time.values()
)
# Apertura y cierre según el primer y último turno
# significativo detectado.
ordered_turns = sorted(
	turns,
	key=lambda item: item["start"]
)
opening_speaker = (
	ordered_turns[0]["speaker"]
	if ordered_turns
	else None
)
closing_speaker = (
	max(
    	ordered_turns,
    	key=lambda item: item["end"]
	)["speaker"]
	if ordered_turns
	else None
)
all_speakers = sorted(
	set(speaking_time)
	| set(alignment_statistics)
)
prominence_results = {}
for speaker in all_speakers:
	speaker_turns = turns_by_speaker[
    	speaker
	]
	turn_durations = [
    	turn["duration"]
    	for turn in speaker_turns
	]
	number_of_turns = len(
    	speaker_turns
	)
	speaker_time = speaking_time[
    	speaker
	]
	speaking_percentage = (
    	speaker_time
    	/ total_speaking_time
    	* 100
    	if total_speaking_time > 0
    	else 0.0
	)
	average_turn_duration = (
    	sum(turn_durations)
    	/ number_of_turns
    	if number_of_turns > 0
    	else 0.0
	)
	maximum_turn_duration = (
    	max(turn_durations)
    	if turn_durations
    	else 0.0
	)
	minimum_turn_duration = (
    	min(turn_durations)
    	if turn_durations
    	else 0.0
	)
	alignment = alignment_statistics[
    	speaker
	]
	evaluated_duration = alignment[
    	"evaluated_duration"
	]
	aligned_duration = alignment[
    	"aligned_duration"
	]
	visual_alignment_time_rate = (
    	aligned_duration
    	/ evaluated_duration
    	* 100
    	if evaluated_duration > 0
    	else 0.0
	)
	evaluated_segments = alignment[
    	"evaluated_segments"
	]
	aligned_segments = alignment[
    	"aligned_segments"
	]
	visual_alignment_segment_rate = (
    	aligned_segments
    	/ evaluated_segments
    	* 100
    	if evaluated_segments > 0
    	else 0.0
	)
	prominence_results[speaker] = {
    	"speaking_time": round(
        	speaker_time,
        	3
    	),
    	"speaking_percentage": round(
        	speaking_percentage,
        	2
    	),
    	"raw_segments": raw_segment_count[
        	speaker
    	],
    	"turns": number_of_turns,
    	"average_turn_duration": round(
        	average_turn_duration,
        	3
    	),
    	"maximum_turn_duration": round(
        	maximum_turn_duration,
        	3
    	),
    	"minimum_turn_duration": round(
        	minimum_turn_duration,
        	3
    	),
    	"opens_video": (
        	speaker == opening_speaker
    	),
    	"closes_video": (
        	speaker == closing_speaker
    	),
    	"visual_alignment": {
        	"evaluated_segments": (
            	evaluated_segments
        	),
        	"aligned_segments": (
            	aligned_segments
        	),
        	"ambiguous_segments": alignment[
            	"ambiguous_segments"
        	],
        	"no_visual_segments": alignment[
            	"no_visual_segments"
        	],
        	"short_segments_excluded": alignment[
            	"short_segments"
        	],
        	"evaluated_duration": round(
            	evaluated_duration,
            	3
        	),
        	"aligned_duration": round(
            	aligned_duration,
            	3
        	),
        	"segment_rate_percentage": round(
            	visual_alignment_segment_rate,
            	2
        	),
        	"time_rate_percentage": round(
            	visual_alignment_time_rate,
            	2
        	)
    	},
    	"turn_details": [
        	{
            	"start": round(
                	turn["start"],
                	3
            	),
            	"end": round(
                	turn["end"],
                	3
            	),
            	"duration": round(
                	turn["duration"],
                	3
            	)
        	}
        	for turn in speaker_turns
    	]
	}
output = {
	"video_id": VIDEO_ID,
	"configuration": {
    	"minimum_segment_duration": (
        	MIN_SEGMENT_DURATION
    	),
    	"maximum_turn_gap": (
        	MAX_TURN_GAP
    	)
	},
	"summary": {
    	"number_of_speakers": len(
        	all_speakers
    	),
    	"total_speaking_time": round(
        	total_speaking_time,
        	3
    	),
    	"opening_speaker": opening_speaker,
    	"closing_speaker": closing_speaker,
    	"valid_audio_segments": len(
        	valid_segments
    	),
    	"merged_turns": len(
        	turns
    	)
	},
	"speakers": prominence_results
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
output,file,ensure_ascii=False,indent=2)
print("\n=== MÉTRICAS DE PROTAGONISMO ===\n")
print(f"Speakers analizados: "f"{len(all_speakers)}")
print(f"Segmentos válidos: "f"{len(valid_segments)}")
print(f"Turnos después de fusionar: "f"{len(turns)}")
print(f"Speaker de apertura: "f"{opening_speaker}")
print(f"Speaker de cierre: "f"{closing_speaker}")
print()
for speaker, metrics in prominence_results.items():
	print(speaker)
	print(f"  Tiempo hablado: "f"{metrics['speaking_time']:.2f} s")
	print(f"  Porcentaje de habla: "f"{metrics['speaking_percentage']:.2f}%")
	print(f"  Turnos: "f"{metrics['turns']}")
	print(f"  Duración media: "f"{metrics['average_turn_duration']:.2f} s")
	print(f"  Turno más largo: "f"{metrics['maximum_turn_duration']:.2f} s")
	print(f"  Abre el vídeo: "f"{metrics['opens_video']}")
	print(f"  Cierra el vídeo: "f"{metrics['closes_video']}")
	print(f"  Alineación visual por tiempo: "f"{metrics['visual_alignment']['time_rate_percentage']:.2f}%")
	print(f"  Alineación visual por segmentos: "f"{metrics['visual_alignment']['segment_rate_percentage']:.2f}%")
	print()
print(f"Resultado guardado en: "f"{OUTPUT_PATH}")

