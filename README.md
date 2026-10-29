# Medición multimodal del protagonismo de las mujeres en paneles y conferencias tecnológicos.
> Quién habla, cuánto, cuándo, con qué visibilidad y qué contenido aporta.

## Equipo 14
** Datitas**
### Autoras:
- Sara Piñas
- Afina Nurova
- Paula Gutiérrez


## Descripción
Este proyecto desarrolla un sistema abierto de análisis multimodal para estudiar cómo se distribuyen la presencia y el protagonismo de las mujeres en conferencias tecnológicas.

El pipeline combina:

- diarización de hablantes;
- transcripción automática;
- detección y tracking de personas;
- alineación entre voz e imagen;
- métricas de presencia y control del turno;
- análisis semántico de las intervenciones mediante OVHcloud AI Endpoints;
- generación de métricas finales por vídeo;
- comparación agregada entre varios vídeos.

El sistema fusiona audio, vídeo y texto para producir métricas interpretables y explorables mediante un dashboard interactivo.

# Resultados principales del MVP
Se han procesado cinco fragmentos audiovisuales con características diferentes:
```text
V001_sample
V002_sample
V003_sample
V004_sample
V005_sample
```
En total se analizaron:
- 5 vídeos
- 30 clusters de voz anotados
- 47 min de habla
- 77 turnos reconstruidos

## Composición documentada
```text
Mujeres: 9/30 participantes
Hombres: 21/30 participantes
```
## Ejecutar únicamente el dashboard

Crear un entorno virtual:

```powershell
py -3.12 -m venv .venv-dashboard
```

Activarlo:

```powershell
.venv-dashboard\Scripts\activate
```

Instalar las dependencias:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Ejecutar desde la raíz del repositorio:

```powershell
python -m streamlit run app.py
```

La aplicación se abrirá normalmente en:

```text
http://localhost:8501
```

## Vistas disponibles

### Resumen

Presenta:

- vídeos analizados;
- clusters de voz;
- tiempo total de habla;
- cobertura de anotación;
- composición del corpus;
- distribución global del tiempo hablado;
- turnos, aperturas y cierres.

### Comparación por vídeo

Permite seleccionar una muestra y explorar:

- número de clusters de voz;
- composición documentada;
- participante o cluster con mayor porcentaje de habla;
- distribución del tiempo hablado;
- alineación voz-imagen;
- tipos de contenido;
- peso técnico estimado.

### Representación y protagonismo

Compara:

- representación numérica;
- cuota total de voz;
- tiempo medio hablado por participante;
- número de turnos;
- aperturas;
- cierres;
- alineación voz-imagen.


### Metodología y transparencia

Documenta:

- arquitectura multimodal;
- tecnologías utilizadas;
- perspectiva de género;
- decisiones éticas;
- limitaciones del sistema;
- riesgos y posibles mejoras.

---

# Arquitectura

El procesamiento se divide en varias capas:

```text
VÍDEO
│
├── AUDIO
│   ├── FFmpeg
│   ├── pyannote
│   └── faster-whisper
│
├── IMAGEN
│   ├── YOLO
│   └── ByteTrack
│
├── FUSIÓN
│   ├── speaker ↔ transcript
│   └── speaker ↔ prominencia visual
│
├── CONTENIDO
│   └── OVHcloud AI Endpoints / Mistral
│
└── ANOTACIÓN
    └── correspondencia manual speaker-participante
```

## Audio

### FFmpeg

Extrae y normaliza el audio del vídeo:

```text
mono
16 kHz
WAV
```

### pyannote

Realiza la diarización y genera clusters de voz:

```text
SPEAKER_00
SPEAKER_01
SPEAKER_02
...
```

Estos identificadores son clusters técnicos de voz, no identidades reales.

### faster-whisper

Genera:

- transcripción;
- idioma detectado;
- timestamps por segmento;
- timestamps por palabra.

---

## Vídeo

### YOLO

Detecta únicamente la clase:

```text
person
```

No se utiliza reconocimiento facial ni clasificación de atributos personales.

### ByteTrack

Relaciona las detecciones entre frames y genera tracklets temporales:

```text
TRACK_01
TRACK_02
TRACK_03
...
```

Un track no equivale a una identidad global. La misma persona puede obtener distintos IDs después de un cambio de plano.

---
## Fusión multimodal

### Speaker-transcript

Las palabras transcritas se asignan al cluster de voz activo mediante sus timestamps.

Resultado:

```text
speaker
+
inicio
+
fin
+
duración
+
texto
```

### Speaker-visual

Durante cada segmento de voz se analizan los tracks visibles mediante:

- cobertura temporal;
- duración visible;
- área relativa;
- centralidad;
- dominancia;
- diferencia entre el primer y segundo candidato.

Estados posibles:

```text
candidate_selected
ambiguous_group_shot
no_visual_candidate
segment_too_short
```

#### `candidate_selected`

Existe una figura visual suficientemente dominante.

#### `ambiguous_group_shot`

Varias personas presentan una prominencia similar y no existe evidencia suficiente para elegir una.

#### `no_visual_candidate`

No existe una detección visual válida.

#### `segment_too_short`

El segmento de audio es demasiado corto para analizarlo de forma fiable.

`candidate_selected` no implica reconocimiento biométrico ni identificación personal.

---

## Análisis semántico

Las intervenciones se analizan mediante OVHcloud AI Endpoints utilizando una API compatible con OpenAI y el modelo virtual:

```text
mistral@latest
```

Cada intervención se clasifica en una categoría:

```text
technical_explanation
answer
question
opinion
moderation
introduction
closing
organizational
other
```

También se estima un peso técnico:

```text
low
medium
high
```

El modelo analiza únicamente texto.

No determina:

- qué persona habla;
- identidad;
- género;
- tiempo de habla;
- presencia visual;
- tracking;
- calidad o mérito de una persona.

El peso técnico es una clasificación semántica experimental, no una medida objetiva de importancia.

---

# Inicio rápido del proyecto completo

## 1. Configurar Python 
El proyecto se ha desarrollado con python 3.12
Crear el entorno virtual:
```powershell
py -3.12 -m venv .venv
```

Activarlo en Windows:

```powershell
.venv\Scripts\activate
```

Actualizar pip:

```powershell
python -m pip install --upgrade pip
```
Instalar las dependencias completas:

```powershell
pip install -r requirements.txt
```
---
## 2. Instalar FFmpeg

Comprobar si está disponible:

```powershell
ffmpeg -version
```

En Windows puede instalarse mediante:

```powershell
winget install Gyan.FFmpeg
```

Después de la instalación puede ser necesario cerrar y volver a abrir la terminal.

## 3. Configurar credenciales

El pipeline necesita dos variables de entorno.

### Hugging Face

Necesaria para cargar el modelo de diarización de pyannote:

```powershell
$env:HF_TOKEN="TU_TOKEN"
```

Comprobar sin mostrar el valor:

```powershell
if ($env:HF_TOKEN) {
    "HF_TOKEN configurado"
} else {
    "HF_TOKEN no configurado"
}
```
---

### OVHcloud AI Endpoints

Necesaria para el análisis semántico:

```powershell
$env:OVH_AI_ENDPOINTS_ACCESS_TOKEN="TU_TOKEN"
```

Comprobar:

```powershell
if ($env:OVH_AI_ENDPOINTS_ACCESS_TOKEN) {
    "Token OVH configurado"
} else {
    "Token OVH no configurado"
}
```

# Preparar un vídeo

Los vídeos se guardan localmente en:

```text
data/raw/
```

Ejemplo:

```text
data/raw/V006.webm
```

Para validar el pipeline se recomienda utilizar un fragmento representativo de entre seis y diez minutos.

Ejemplo:

```powershell
ffmpeg -ss 00:12:30 -i data/raw/V006.webm -t 00:08:00 -c copy data/raw/V006_sample.webm
```

Comprobar el sample:

```powershell
ffprobe data/raw/V006_sample.webm
```

Es recomendable seleccionar fragmentos con:

- varios participantes;
- cambios de hablante;
- conversación o debate real;
- planos individuales y grupales;
- cambios de cámara.

Conviene evitar:

- introducciones largas de una sola persona;
- presentaciones individuales consecutivas;
- vídeos congelados;
- fragmentos formados principalmente por diapositivas.

---
# Ejecutar el pipeline
Una vez disponible:
```text
data/raw/V006_sample.webm
```

ejecutar:

```powershell
python scripts/run_pipeline.py V006_sample
```

El argumento corresponde al `VIDEO_ID` y no debe incluir la extensión.

Correcto:

```powershell
python scripts/run_pipeline.py V006_sample
```

Incorrecto:

```powershell
python scripts/run_pipeline.py V006_sample.webm
```

El resultado principal será:

```text
outputs/V006_sample_final_metrics.json
```

---

# Reanudación automática

El pipeline comprueba si cada resultado ya existe.

Ejemplo:

```text
[SKIP] Extracción de audio
       Ya existe: data/audio/V006_sample.wav

[SKIP] Diarización
       Ya existe: outputs/V006_sample_diarization.json
```

Esto permite reanudar una ejecución sin repetir operaciones costosas.

Para recalcular un paso concreto, se puede eliminar previamente su fichero de salida correspondiente.

---
# Outputs

Para un vídeo identificado como `V006_sample` se generan:

```text
data/audio/
└── V006_sample.wav

outputs/
├── V006_sample_diarization.json
├── V006_sample_transcription.json
├── V006_sample_tracks.json
├── V006_sample_speaker_visual_alignment.json
├── V006_sample_speaker_transcript.json
├── V006_sample_prominence.json
├── V006_sample_content_analysis.json
└── V006_sample_final_metrics.json
```

## Resultado final por speaker

`*_final_metrics.json` agrupa:

```text
presence
├── speaking_time_seconds
└── speaking_percentage

turn_control
├── turns
├── average_turn_duration_seconds
├── maximum_turn_duration_seconds
├── opens_video
└── closes_video

visual
├── alignment_time_percentage
├── alignment_segment_percentage
└── ambiguous_segments

content
├── segments_analyzed
├── dominant_content_type
├── content_type_counts
└── duration_by_content_type_seconds

technical_weight
├── counts
├── duration_seconds
└── time_percentage
```

Las métricas semánticas se ponderan por duración. Un segmento de 90 segundos tiene más peso que uno de tres segundos.

---

# Agregación de resultados

## Comparación entre vídeos

```powershell
python src/metrics/aggregate_metrics.py V001_sample V002_sample V003_sample V004_sample V005_sample
```

Resultado:

```text
outputs/aggregate_metrics.json
```

La agregación incluye:

- número de clusters de voz;
- cluster con mayor porcentaje de habla;
- distribución del tiempo;
- alineación visual media;
- distribución de contenido;
- peso técnico estimado.

Los IDs de speaker son locales a cada vídeo.

```text
V001_sample / SPEAKER_01
```

no representa necesariamente a la misma persona que:

```text
V002_sample / SPEAKER_01
```
## Métricas por género documentado

```powershell
python src/metrics/gender_metrics.py V001_sample V002_sample V003_sample V004_sample V005_sample
```

Resultado:

```text
outputs/gender_metrics.json
```

---

# Anotación de participantes

La relación entre clusters de voz y participantes está documentada en:

```text
config/participants.json
```

Ejemplo:

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

Los identificadores de participante son locales a cada vídeo.

```text
V001_sample / participant_01
```

no representa necesariamente a la misma persona que:

```text
V002_sample / participant_01
```

La relación speaker-participante se revisa manualmente mediante varios intervalos de audio y vídeo.

---

# Casos audiovisuales del MVP

## V001

Panel con varios participantes y cambios de plano.

## V002

Panel acompañado de una ronda de preguntas y voces de la audiencia fuera de plano.

## V003

Panel con varios participantes y una realización audiovisual dinámica.

## V004

Panel presencial con plano grupal persistente.

## V005

Panel con varias personas visibles simultáneamente.

V004 y V005 producen principalmente:

```text
ambiguous_group_shot
```

Esto no significa que las personas no estén visibles. Significa que la realización no permite seleccionar de manera fiable una única figura visual dominante.

---
# OCR opcional

Existe un módulo experimental de OCR:

```text
src/ocr/extract_labels.py
```

Se utiliza únicamente cuando el vídeo contiene rótulos visibles con nombres o roles.

En vídeos sin rótulos no se intenta inferir identidad mediante atributos visuales.

---

# Ética y privacidad

El proyecto sigue los siguientes principios:

- no utiliza reconocimiento facial;
- no utiliza biometría para identificar participantes;
- no infiere género a partir de imágenes;
- no infiere género a partir de voz;
- no infiere género a partir de nombres;
- los track IDs son anónimos y temporales;
- los clusters de voz son identificadores técnicos;
- las asociaciones ambiguas no se fuerzan;
- la categoría `unknown` se conserva cuando no existe evidencia;
- los resultados se presentan de forma agregada;
- la clasificación semántica se limita al texto.

La perspectiva de género condiciona tanto las métricas como las decisiones de diseño del sistema.

---
# Limitaciones

- El corpus contiene únicamente cinco fragmentos seleccionados.
- Los resultados no representan todas las conferencias tecnológicas.
- Pyannote puede generar microsegmentos o fragmentar una misma voz.
- Los cambios de cámara pueden fragmentar los tracklets.
- Las preguntas de la audiencia pueden no tener representación visual.
- Los planos grupales pueden producir `ambiguous_group_shot`.
- La alineación voz-imagen no equivale a presencia visual.
- La clasificación semántica depende del modelo utilizado.
- La asociación speaker-participante requiere revisión humana.
- La validación experimental debe ampliarse con métricas formales de diarización, transcripción y alineación.

---

# Estructura del repositorio

```text
.
├── app.py
├── dashboard/
├── scripts/
│   └── run_pipeline.py
├── src/
│   ├── audio/
│   ├── fusion/
│   ├── metrics/
│   ├── ocr/
│   ├── semantic/
│   └── video/
├── config/
│   ├── participants.json
│   └── videos.json
├── outputs/
├── data/
├── .streamlit/
├── requirements.txt
├── requirements-dashboard.txt
├── LICENSE
└── README.md
```

---

# Dependencias de terceros

Principales componentes utilizados:

| Componente | Uso |
|---|---|
| FFmpeg | Extracción y normalización de audio |
| pyannote.audio | Diarización |
| faster-whisper | Transcripción |
| Ultralytics YOLO | Detección de personas |
| ByteTrack | Tracking temporal |
| OpenCV | Procesamiento de vídeo |
| EasyOCR | OCR opcional |
| OVHcloud AI Endpoints | Acceso al modelo semántico |
| Mistral | Clasificación semántica |
| Streamlit | Dashboard |
| Plotly | Visualización |

Las licencias concretas de las dependencias y de los vídeos utilizados deben revisarse en sus fuentes oficiales antes de reutilizar o redistribuir material.

---

# Licencia

El código del proyecto se distribuye bajo la licencia indicada en:

text
LICENSE


Los vídeos y datasets mantienen sus propias licencias y condiciones de uso.

La licencia del código no modifica ni sustituye las licencias aplicables al material audiovisual o a los modelos de terceros.
