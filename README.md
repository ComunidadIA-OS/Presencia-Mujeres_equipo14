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
  "end": 118*882,
  "duration": 22.883
}
```

*os identificadores:

```text
SPEAK*R_00
SPE*KER_01
SPEAKER_02
...
```

represe*tan clusters de voz.

No represent*n identidades reales.

---

# 2. T*anscripción

La transcripción se r*aliza mediante faster-whisper.

Ou*put:

```text
*_transcription.json*```

Se generan:

- texto transcri*o;
- timestamps;
- timestamps a ni*el de palabra;
- idioma detectado.*
Estos timestamps permiten posteri*rmente relacionar las palabras con*los segmentos producidos por pyann*te.

---

# 3. Detección de person*s

La detección visual utiliza YOL* y únicamente la clase:

```text
p*rson
```

No se utiliza reconocimi*nto facial.

No se realiza clasifi*ación de género sobre las imágenes*

---

# 4. Tracking

El tracking *tiliza ByteTrack.

Output:

```tex*
*_tracks.json
```

Los IDs genera*os representan tracklets temporale*.

Por ejemplo:

```text
TRACK_037*TRACK_090
TRACK_172
```

Un mismo *articipante puede recibir distinto* IDs después de cambios de plano.
*Por tanto:

```text
TRACK_ID != id*ntidad global
```

---

# 5. Aline*ción voz-imagen

Output:

```text
*_speaker_visual_alignment.json
```*
Durante cada segmento de voz se a*alizan las personas visibles.

La *rominencia visual utiliza informac*ón como:

- tiempo visible;
- área*relativa del bounding box;
- centr*lidad;
- dominancia visual;
- dife*encia respecto al siguiente candid*to.

Estados posibles:

```text
ca*didate_selected
ambiguous_group_sh*t
no_visual_candidate
segment_too_*hort
```

## candidate_selected

E*iste una figura visual suficientem*nte dominante durante ese segmento*

## ambiguous_group_shot

Hay var*as personas visibles y no existe s*ficiente evidencia para selecciona* una.

## no_visual_candidate

No *xiste una detección visual que cum*la los criterios.

## segment_too_*hort

El segmento de audio es dema*iado corto para utilizarlo de form* fiable.

IMPORTANTE:

```text
can*idate_selected
```

no significa q*e se haya identificado biométricam*nte a la persona que habla.

Repre*enta únicamente un candidato visua* basado en prominencia temporal y *spacial.

---

# 6. Alineación spe*ker-transcript

Output:

```text
**speaker_transcript.json
```

Combi*a:

```text
speaker
+
inicio
+
fin*+
duración
+
texto
```

Las palabr*s transcritas se asignan a los seg*entos de diarización mediante sus *imestamps.

---

# 7. Métricas de *rotagonismo

Output:

```text
*_pr*minence.json
```

Actualmente se c*lculan:

- tiempo total de habla;
* porcentaje de tiempo hablado;
- n*mero de turnos;
- duración media d* turno;
- duración máxima de turno*
- speaker de apertura;
- speaker *e cierre;
- alineación visual por *iempo;
- alineación visual por seg*entos.

Los microsegmentos inferio*es al umbral configurado se excluy*n de estas métricas derivadas.

Ta*bién se fusionan segmentos consecu*ivos del mismo speaker cuando está* separados por pausas suficienteme*te pequeñas.

---

# 8. Análisis s*mántico

Output:

```text
*_conten*_analysis.json
```

El análisis ut*liza OVHcloud AI Endpoints mediant* una API compatible con OpenAI.

A*tualmente el pipeline utiliza el m*delo virtual:

```text
mistral@lat*st
```

Durante las pruebas, OVH r*solvió este modelo virtual a un mo*elo Mistral disponible en su servi*io.

El LLM clasifica cada interve*ción en una categoría:

```text
te*hnical_explanation
answer
question*opinion
moderation
introduction
cl*sing
organizational
other
```

Tam*ién estima el peso técnico:

```te*t
low
medium
high
```

IMPORTANTE:*
El LLM únicamente analiza el text*.

El LLM no determina:

- quién e*tá hablando;
- identidad;
- género*
- presencia visual;
- tiempo de h*bla;
- tracking.

---

# 9. Métric*s finales

El resultado principal *e cada vídeo es:

```text
*_final_*etrics.json
```

Para cada `SPEAKE*_XX` se agrupan:

```text
presence*├── speaking_time_seconds
└── spea*ing_percentage

turn_control
├── t*rns
├── average_turn_duration_seco*ds
├── maximum_turn_duration_secon*s
├── opens_video
└── closes_video*
visual
├── alignment_time_percent*ge
├── alignment_segment_percentag*
└── ambiguous_segments

content
├*─ segments_analyzed
├── dominant_c*ntent_type
├── content_type_counts*└── duration_by_content_type_secon*s

technical_weight
├── counts
├──*duration_seconds
└── time_percenta*e
```

Las métricas semánticas se *gregan también por duración.

Así,*un segmento de 90 segundos tiene m*s peso que otro de 3 segundos.

--*

# Comparar varios vídeos

Cuando*ya existen varios resultados final*s se puede ejecutar:

```powershel*
python src/metrics/aggregate_metr*cs.py V001_sample V002_sample
```
*Para cinco vídeos:

```powershell
*ython src/metrics/aggregate_metric*.py V001_sample V002_sample V003_s*mple V004_sample V005_sample
```

*e genera:

```text
outputs/aggrega*e_metrics.json
```

La agregación *ompara actualmente:

- número de s*eakers;
- speaker con mayor porcen*aje de habla;
- distribución del t*empo de habla;
- alineación visual*media;
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

# Próximos pasos

1. Seleccionar y procesar `V003_sample`.
2. Seleccionar y procesar `V004_sample`.
3. Seleccionar y procesar `V005_sample`.
4. Validar manualmente una selección de segmentos de cada vídeo.
5. Consolidar las métricas agregadas.
6. Incorporar información declarada de participantes cuando exista una fuente verificable.
7. Incorporar género declarado sin inferencia biométrica.
8. Generar visualizaciones finales.
9. Documentar limitaciones y metodología.
10. Preparar demo y presentación final.
