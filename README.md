# Challenge Mujeres IA - Análisis multimodal de conferencias técnicas

Este proyecto desarrolla un sistema abierto para analizar vídeos de conferencias y paneles técnicos y estudiar la distribución de presencia y protagonismo entre las personas participantes.

El pipeline combina:

- diarización de hablantes;
- transcripción automática;
- detección y tracking de personas;
- alineación entre voz e imagen;
- métricas de presencia y control del turno;
- análisis semántico de las intervenciones mediante OVHcloud AI Endpoints;
- generación de métricas finales por vídeo;
- comparación agregada entre varios vídeos.

> Importante: el sistema no utiliza reconocimiento facial ni infiere género mediante imagen, voz o apariencia.

---

# Estado actual

Actualmente se han procesado correctamente dos muestras independientes:

- `V001_sample`
- `V002_sample`

Ambas producen las métricas finales utilizando el mismo pipeline automatizado.

El siguiente objetivo del MVP es completar un conjunto de cinco muestras heterogéneas y generar su comparación agregada.

---

# Quick start

## 1. Clonar el repositorio

Clonar el repositorio y acceder al proyecto:

```powershell
git clone <URL_DEL_REPOSITORIO>
cd ChallengeMujeresIA
```

Actualizar las ramas remotas:

```powershell
git fetch origin
```

Cambiar a la rama actual de desarrollo:

```powershell
git switch multimodal-pipeline
```

---

# 2. Configurar Python

El proyecto se ha desarrollado con Python 3.12.

Comprobar la versión instalada:

```powershell
python --version
```

Se recomienda:

```text
Python 3.12.x
```

Crear el entorno virtual:

```powershell
py -3.12 -m venv .venv
```

Activarlo en Windows:

```powershell
.venv\Scripts\activate
```

La terminal debería mostrar algo parecido a:

```text
(.venv) PS C:\...\ChallengeMujeresIA>
```

---

# 3. Instalar las dependencias

Actualizar pip:

```powershell
python -m pip install --upgrade pip
```

Instalar las dependencias:

```powershell
pip install -r requirements.txt
```

Entre las dependencias principales utilizadas actualmente están:

```text
pyannote.audio
ultralytics
faster-whisper
av<19
opencv-python
openai
easyocr
```

Se utiliza `av<19` porque durante el desarrollo se encontró una incompatibilidad entre la versión utilizada de faster-whisper y versiones posteriores de PyAV.

---

# 4. Instalar FFmpeg

Comprobar primero si FFmpeg está instalado:

```powershell
ffmpeg -version
```

Si no está instalado en Windows:

```powershell
winget install Gyan.FFmpeg
```

Después de instalarlo puede ser necesario cerrar y volver a abrir la terminal.

---

# 5. Configurar los tokens

El pipeline necesita dos tokens.

## Hugging Face

Se utiliza para cargar el modelo de diarización de pyannote.

En PowerShell:

```powershell
$env:HF_TOKEN="TU_TOKEN"
```

Comprobar que existe sin mostrar su contenido:

```powershell
if ($env:HF_TOKEN) {
    "HF OK"
} else {
    "HF NO configurado"
}
```

---

## OVHcloud AI Endpoints

Se utiliza para el análisis semántico de las transcripciones.

Configurar:

```powershell
$env:OVH_AI_ENDPOINTS_ACCESS_TOKEN="TU_TOKEN"
```

Comprobar:

```powershell
if ($env:OVH_AI_ENDPOINTS_ACCESS_TOKEN) {
    "OVH OK"
} else {
    "OVH NO configurado"
}
```

IMPORTANTE:

- no escribir tokens directamente en los scripts;
- no subir tokens a GitHub;
- no poner tokens en este README;
- no incluir tokens dentro de commits.

Las variables configuradas con `$env:` permanecen en la sesión actual de PowerShell.

Si se abre una terminal nueva será necesario configurarlas otra vez.

---

# Preparar un vídeo

Los vídeos se guardan localmente en:

```text
data/raw/
```

Por ejemplo:

```text
data/raw/V003.webm
```

Para desarrollar y validar el pipeline es recomendable utilizar fragmentos representativos en lugar de procesar siempre el vídeo completo.

Por ejemplo, para extraer 8 minutos empezando en `00:12:30`:

```powershell
ffmpeg -ss 00:12:30 -i data/raw/V003.webm -t 00:08:00 -c copy data/raw/V003_sample.webm
```

Esto generará:

```text
data/raw/V003_sample.webm
```

Comprobar el sample:

```powershell
ffprobe data/raw/V003_sample.webm
```

Para los samples interesa seleccionar intervalos donde haya:

- varios participantes;
- varios cambios de hablante;
- planos individuales y grupales;
- cambios de cámara;
- conversación, debate o panel real.

Conviene evitar:

- introducciones largas de una sola persona;
- presentaciones individuales consecutivas;
- vídeos con imagen estática;
- largos fragmentos de diapositivas sin participantes.

---

# Ejecutar el pipeline completo

Una vez disponible, por ejemplo:

```text
data/raw/V003_sample.webm
```

ejecutar:

```powershell
python scripts/run_pipeline.py V003_sample
```

IMPORTANTE:

El argumento es el `VIDEO_ID`.

Correcto:

```powershell
python scripts/run_pipeline.py V003_sample
```

Incorrecto:

```powershell
python scripts/run_pipeline.py V003_sample.webm
```

---

# Pipeline

`run_pipeline.py` ejecuta automáticamente el flujo completo:

```text
VÍDEO
  |
  v
Extracción de audio
  |
  +-------------------------+
  |                         |
  v                         v
Diarización              Detección
pyannote                    YOLO
  |                         |
  v                         v
Speakers                  ByteTrack
  |                         |
  +-----------+-------------+
              |
              v
      Alineación voz-imagen
              |
              v
         Transcripción
       faster-whisper
              |
              v
 Alineación speaker-transcript
              |
              v
 Métricas de protagonismo
              |
              v
Análisis semántico con OVH
              |
              v
       Métricas finales
```

El resultado principal será:

```text
outputs/V003_sample_final_metrics.json
```

---

# Reanudación automática

El pipeline comprueba si determinados resultados ya existen antes de ejecutar cada paso.

Por ejemplo:

```text
[SKIP] Extracción de audio
       Ya existe: data/audio/V003_sample.wav

[SKIP] Diarización
       Ya existe: outputs/V003_sample_diarization.json
```

Esto permite volver a ejecutar:

```powershell
python scripts/run_pipeline.py V003_sample
```

sin recalcular todos los pasos anteriores.

Si se quiere recalcular expresamente un paso, se puede eliminar previamente su fichero de salida correspondiente.

---

# Outputs generados

Para un vídeo identificado como:

```text
V003_sample
```

se generan:

```text
data/audio/
└── V003_sample.wav

outputs/
├── V003_sample_diarization.json
├── V003_sample_transcription.json
├── V003_sample_tracks.json
├── V003_sample_speaker_visual_alignment.json
├── V003_sample_speaker_transcript.json
├── V003_sample_prominence.json
├── V003_sample_content_analysis.json
└── V003_sample_final_metrics.json
```

---

# 1. Diarización

La diarización se realiza con pyannote.

Output:

```text
*_diarization.json
```

Ejemplo:

`*`json
*
  "speaker": "SPEAKER_03",
* "start": 95.999,
  "end": 118.882,
  "duration": 22.883
}
```

Los identificadores:

```text
SPEAKER_00
SPEAKER_01
SPEAKER_02
...
```

representan clusters de voz.

No representan identidades reales.

---

# 2. Transcripción

La transcripción se realiza mediante faster-whisper.

Output:

```text
*_transcription.json*```

Se generan:

- texto transcrito;
- timestamps;
- timestamps a nivel de palabra;
- idioma detectado.
Estos timestamps permiten posteriormente relacionar las palabras con los segmentos producidos por pyannote.

---

# 3. Detección de personas

La detección visual utiliza YOLO y únicamente la clase:

```text
person
```

No se utiliza reconocimiento facial.

No se realiza clasificación de género sobre las imágenes

---

# 4. Tracking

El tracking utiliza ByteTrack.

Output:

```text
_tracks.json
```

Los IDs generados representan tracklets temporales.

Por ejemplo:

```text
TRACK_037_TRACK_090
TRACK_172
```

Un mismo participante puede recibir distintos IDs después de cambios de plano.
Por tanto:

```text
TRACK_ID != identidad global
```

---

# 5. Alineación voz-imagen

Output:

```text
_speaker_visual_alignment.json
```
Durante cada segmento de voz se analizan las personas visibles.

La prominencia visual utiliza información como:

- tiempo visible;
- área relativa del bounding box;
- centrtlidad;
- dominancia visual;
- diferencia respecto al siguiente candidato.

Estados posibles:

```text
candidate_selected
ambiguous_group_shot
no_visual_candidate
segment_too_short
```

## candidate_selected

Elegiste una figura visual suficientemente dominante durante ese segmento.

## ambiguous_group_shot

Hay varias personas visibles y no existe suficiente evidencia para seleccionar una.

## no_visual_candidate

No existe una detección visual que cumpla los criterios.

## segment_too_short

El segmento de audio es demasiado corto para utilizarlo de forma fiable.

IMPORTANTE:

```text
candidate_selected
```

no significa que se haya identificado biométricamente a la persona que habla.

Representa únicamente un candidato visual basado en prominencia temporal y espacial.

---

# 6. Alineación speaker-transcript

Output:

```text
speaker_transcript.json
```

Combina:

```text
speaker
+
inicio
+
fin+
duración
+
texto
```

Las palabras transcritas se asignan a los segmentos de diarización mediante sus timestamps.

---

# 7. Métricas de protagonismo

Output:

```text
_prominence.json
```

Actualmente se calculan:

- tiempo total de habla;
- porcentaje de tiempo hablado;
- numero de turnos;
- duración media de turno;
- duración máxima de turn;
- speaker de apertura;
- speaker de cierre;
- alineación visual por tiempo;
- alineación visual por segmentos.

Los microsegmentos inferiores al umbral configurado se excluyen de estas métricas derivadas.

También se fusionan segmentos consecutivos del mismo speaker cuando están separados por pausas suficientemente pequeñas.

---

# 8. Análisis semántico

Output:

```text
_content_analysis.json
```

El análisis utuliza OVHcloud AI Endpoints mediante una API compatible con OpenAI.

Actualmente el pipeline utiliza el modelo virtual:

```text
mistral@latest
```

Durante las pruebas, OVH resolvió este modelo virtual a un modelo Mistral disponible en su servicio.

El LLM clasifica cada intervención en una categoría:

```text
technical_explanation
answer
question-opinion
moderation
introduction
closing
organizational
other
```

También estima el peso técnico:

```text
low
medium
high
```

IMPORTANTE:
El LLM únicamente analiza el text.

El LLM no determina:

- quién está hablando;
- identidad;
- género;
- presencia visual;
- tiempo de habla;
- tracking.

---

# 9. Métricas finales

El resultado principal de cada vídeo es:

```text
_final_metrics.json
```

Para cada `SPEAKER_XX` se agrupan:

```text
presence├── speaking_time_seconds
└── speaking_percentage

turn_control
├── turns
├── average_turn_duration_seconds
├── maximum_turn_duration_seconds
├── opens_video
└── closes_video
visual
├── alignment_time_percentege
├── alignment_segment_percentage
└── ambiguous_segments

content
├─ segments_analyzed
├── dominant_content_type
├── content_type_counts── duration_by_content_type_seconds

technical_weight
├── counts
├──duration_seconds
└── time_percentage
```

Las métricas semánticas se agregan también por duración.

Así, un segmento de 90 segundos tiene más peso que otro de 3 segundos.

--

# Comparar varios vídeos

Cuando ya existen varios resultados finales se puede ejecutar:

```powershel
python src/metrics/aggregate_metrics.py V001_sample V002_sample
```
*Para cinco vídeos:

```powershell
python src/metrics/aggregate_metrics.py V001_sample V002_sample V003_sample V004_sample V005_sample
```

Se genera:

```text
outputs/aggregate_metrics.json
```

La agregación compara actualmente:

- número de speakers;
- speaker con mayor porcentaje de habla;
- distribución del tiempo de habla;
- alineación visual media;
- distribución de tipos de contenido;
- distribución del peso técnico.

Los IDs de speaker son locales a cada vídeo.

Por tanto:

```text
V001 SPEAKER_01
```

no tiene por qué corresponder a:

```text
V002 SPEAKER_01
```

---

# Caso especial: preguntas del público

Un vídeo puede contener, por ejemplo:

```text
4 panelistas visibles
+
preguntas del público fuera de plano
```

Pyannote puede detectar más de cuatro speakers porque también está detectando las voces del público.

Esto no se considera automáticamente un error.

Permite diferenciar conceptualmente entre:

```text
presencia oral
```

y:

```text
representación visual
```

Una persona puede intervenir oralmente sin aparecer claramente en pantalla.

---

# OCR

Existe una prueba de OCR mediante EasyOCR:

```text
src/ocr/extract_labels.py
```

El OCR es un módulo opcional.

Solo se utiliza cuando el vídeo contiene rótulos visibles con información textual como nombre o rol.

En vídeos sin rótulos no se intenta inferir identidad mediante otros atributos visuales.

---

# Resultados actuales

## V001_sample

En la primera muestra se detectaron 4 clusters de voz.

El speaker con mayor tiempo de habla representa aproximadamente el 46 % del habla detectada.

El contenido agregado se distribuyó principalmente entre:

- opinion;
- technical_explanation;
- question;
- moderation.

---

## V002_sample

La segunda muestra contiene un panel acompañado de una ronda de preguntas.

Se detectaron más clusters de voz que panelistas principales visibles porque aparecen intervenciones del público fuera de plano.

Este caso permite probar el comportamiento del pipeline cuando:

```text
número de voces detectadas
!=
número de panelistas visibles
```

---

# Estructura del proyecto

```text
ChallengeMujeresIA/
│
├── scripts/
│   └── run_pipeline.py
│
├── src/
│   ├── audio/
│   │   ├── diarization.py
│   │   └── transcription.py
│   │
│   ├── fusion/
│   │   ├── speaker_visual_alignment.py
│   │   └── speaker_transcript_alignment.py
│   │
│   ├── metrics/
│   │   ├── presence.py
│   │   ├── prominence.py
│   │   ├── final_metrics.py
│   │   └── aggregate_metrics.py
│   │
│   ├── ocr/
│   │   └── extract_labels.py
│   │
│   ├── semantic/
│   │   ├── test_ovh.py
│   │   └── content_analysis.py
│   │
│   └── video/
│       ├── person_detection.py
│       └── person_tracking.py
│
├── config/
├── data/
├── outputs/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Ética y privacidad

El proyecto sigue los siguientes principios:

- no utiliza reconocimiento facial;
- no utiliza biometría para identificar participantes;
- no infiere género a partir de imágenes;
- no infiere género a partir de voz;
- no infiere género a partir de nombres;
- los IDs visuales son anónimos y temporales;
- los clusters de voz son identificadores técnicos;
- la ausencia de evidencia visual se conserva como ambigüedad;
- no se fuerza una asociación cuando la evidencia es insuficiente;
- el género únicamente podrá incorporarse mediante información explícitamente declarada y verificable.

---

# Git

El desarrollo principal se encuentra actualmente en:

```text
multimodal-pipeline
```

Cambiar a la rama:

```powershell
git switch multimodal-pipeline
```

Actualizar:

```powershell
git pull --rebase origin multimodal-pipeline
```

Guardar nuevos cambios:

```powershell
git status
git add .
git commit -m "Descripción del cambio"
git push
```

Antes de hacer commit siempre comprobar:

```powershell
git status
```

No deben subirse:

```text
.venv/
data/raw/
data/audio/
outputs/
*.webm
*.wav
*.pt
.env
```

---

# Flujo recomendado para añadir un nuevo vídeo

## Paso 1

Guardar el vídeo:

```text
data/raw/V003.webm
```

## Paso 2

Localizar visualmente un intervalo representativo.

## Paso 3

Crear el sample:

```powershell
ffmpeg -ss 00:12:30 -i data/raw/V003.webm -t 00:08:00 -c copy data/raw/V003_sample.webm
```

## Paso 4

Configurar los tokens:

```powershell
$env:HF_TOKEN="..."
$env:OVH_AI_ENDPOINTS_ACCESS_TOKEN="..."
```

## Paso 5

Ejecutar:

```powershell
python scripts/run_pipeline.py V003_sample
```

## Paso 6

Comprobar:

```text
outputs/V003_sample_final_metrics.json
```

## Paso 7

Añadirlo a la agregación:

```powershell
python src/metrics/aggregate_metrics.py V001_sample V002_sample V003_sample
```

---

# Estado actual del MVP

El MVP multimodal está completo para cinco muestras de vídeo:

```text
V001_sample
V002_sample
V003_sample
V004_sample
V005_sample
```

Para cada muestra se ha ejecutado el pipeline completo:

```text
vídeo
  ↓
extracción de audio
  ↓
diarización
  ↓
transcripción
  ↓
detección y tracking de personas
  ↓
alineación voz-imagen
  ↓
alineación speaker-transcripción
  ↓
métricas de presencia y protagonismo
  ↓
análisis semántico
  ↓
métricas finales
```

Los resultados individuales se encuentran en:

```text
outputs/V001_sample_final_metrics.json
outputs/V002_sample_final_metrics.json
outputs/V003_sample_final_metrics.json
outputs/V004_sample_final_metrics.json
outputs/V005_sample_final_metrics.json
```

La comparación entre vídeos se genera con:

```powershell
python src/metrics/aggregate_metrics.py V001_sample V002_sample V003_sample V004_sample V005_sample
```

Resultado:

```text
outputs/aggregate_metrics.json
```

---

# Casos audiovisuales incluidos

Las cinco muestras se seleccionaron para representar situaciones diferentes:

```text
V001_sample
Panel con varios participantes y cambios de plano.

V002_sample
Panel con ronda de preguntas e intervenciones fuera de plano.

V003_sample
Panel adicional con varios speakers y una realización audiovisual distinta.

V004_sample
Panel presencial con plano grupal persistente y cuatro participantes visibles.

V005_sample
Panel con cinco speakers y composición grupal o en mosaico.
```

V004 y V005 producen principalmente:

```text
ambiguous_group_shot
```

Esto ocurre porque varias personas permanecen visibles simultáneamente y ninguna domina visualmente de forma suficiente.

Por tanto:

```text
alineación voz-imagen = 0 %
```

no significa:

```text
presencia visual = 0 %
```

Significa que el sistema no puede atribuir de forma suficientemente fiable la voz activa a una única figura visual dominante.

---

# Anotación manual de participantes

La relación entre los clusters de voz y los participantes está documentada manualmente en:

```text
config/participants.json
```

La estructura utilizada es:

```json
{
  "V001_sample": {
    "SPEAKER_00": {
      "participant": "participant_01",
      "declared_gender": "woman",
      "speaker_mapping_verified": true,
      "speaker_mapping_method": "manual_audio_video_review",
      "gender_source": "official_participant_profile"
    }
  }
}
```

## Significado de los campos

```text
participant
Identificador anónimo de participante dentro de un vídeo.

declared_gender
Categoría documentada en una fuente oficial.

speaker_mapping_verified
Indica si la relación SPEAKER_XX ↔ participante fue revisada manualmente.

speaker_mapping_method
Método utilizado para comprobar la correspondencia.

gender_source
Tipo de fuente utilizada para documentar el género.
```

Los IDs de participante son locales a cada vídeo.

Por ejemplo:

```text
V001_sample / participant_01
```

no representa necesariamente a la misma persona que:

```text
V002_sample / participant_01
```

## Principio ético

El género no se obtiene mediante:

```text
apariencia
voz
nombre
reconocimiento facial
clasificación automática
LLM
```

La asociación `SPEAKER_XX ↔ participante` se realiza mediante revisión manual de audio y vídeo.

El género solo se incorpora desde información documentada. Cuando no existe evidencia suficiente, debe utilizarse:

```text
unknown
```

---

# Métricas agregadas por género

Las métricas se generan con:

```powershell
python src/metrics/gender_metrics.py V001_sample V002_sample V003_sample V004_sample V005_sample
```

Resultado:

```text
outputs/gender_metrics.json
```

## Resultados actuales

Se han analizado:

```text
5 vídeos
30 clusters de voz
2.834,92 segundos de habla
aproximadamente 47 minutos y 15 segundos
```

La cobertura declarada actualmente es:

```text
30 speakers con mapping verificado
100 % del tiempo hablado con mapping anotado
```

Distribución del tiempo de habla:

```text
woman
1.017,00 segundos
35,87 % del tiempo hablado

man
1.817,92 segundos
64,13 % del tiempo hablado
```

Control de turnos:

```text
woman
27 turnos
2 aperturas
2 cierres

man
50 turnos
3 aperturas
3 cierres
```

Alineación voz-imagen:

```text
woman
28,33 %

man
29,37 %
```

## Interpretación correcta

Los resultados no se deben presentar como una conclusión general sobre todas las conferencias técnicas.

La formulación recomendada es:

> En los cinco fragmentos seleccionados para el MVP, las intervenciones asociadas manualmente a participantes documentadas como mujeres representan el 35,87 % del tiempo de habla analizado.

La alineación voz-imagen tampoco representa tiempo total visible.
