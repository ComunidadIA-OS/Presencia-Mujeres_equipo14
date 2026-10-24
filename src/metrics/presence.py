import json
from collections import defaultdict

INPUT_PATH = "./data/output/V001_sample_diarization.json"

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    diarization_data = json.load(f)

speaking_time = defaultdict(float)
turn_count = defaultdict(int)

for segment in diarization_data:
    speaker = segment["speaker"]
    duration = segment["duration"]
    speaking_time[speaker] += duration
    turn_count[speaker] += 1

total_speaking_time = sum(speaking_time.values())

print("\n=== Presencia de los hablantes ===")

for speaker in sorted(speaking_time):
    seconds = speaking_time[speaker]

    percentage = (seconds / total_speaking_time* 100 if total_speaking_time > 0 else 0) 

    print(f"{speaker}")
    print(f"  Tiempo de habla: {seconds:.2f} segundos")
    print(f"  Porcentaje de presencia: {percentage:.2f}%")
    print(f"Segmentos: {turn_count[speaker]}")
    print()

print(f"Tiempo total de habla: {total_speaking_time:.2f} segundos")
print(f"Número de speakers: {len(speaking_time)}")
          