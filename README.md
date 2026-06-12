# 🎙️ Transcriptor de Audio con Whisper + Groq

Aplicación de escritorio desarrollada en Python que permite transcribir archivos de audio y video utilizando **OpenAI Whisper**, mejorar automáticamente el texto mediante **IA de Groq (LLaMA 3.3 70B)** y exportar el resultado en un **PDF profesional**.

Ideal para estudiantes, docentes, reuniones, entrevistas, clases grabadas, conferencias y cualquier contenido de audio que necesite convertirse en texto legible.

---

## ✨ Características

### 🎧 Transcripción automática

* Compatible con audio y video.
* Utiliza Whisper para convertir voz a texto.
* Soporta múltiples formatos multimedia.

### 🤖 Mejora opcional con IA

* Corrección ortográfica automática.
* Mejora de puntuación.
* Organización en párrafos coherentes.
* Corrección contextual de palabras mal transcritas.
* Mantiene el contenido original sin inventar información.

### 📄 Exportación profesional a PDF

* Diseño elegante y limpio.
* Fecha de generación automática.
* Nombre del archivo original.
* Indicador visual cuando el texto fue mejorado con IA.
* Formato listo para estudiar, imprimir o compartir.

### 🖥️ Interfaz moderna

* Construida con CustomTkinter.
* Tema oscuro elegante.
* Fácil de usar.
* Vista previa del resultado antes de cerrar la aplicación.

### ⚙️ Gestión automática de FFmpeg

* Detección automática de FFmpeg.
* Configuración manual en caso necesario.

### 🔐 Gestión de API Key

* Guarda localmente la API Key de Groq.
* Carga automática al iniciar la aplicación.

---

# 📸 Vista General del Flujo

```text
Audio/Video
      │
      ▼
 Conversión WAV
    (FFmpeg)
      │
      ▼
 Transcripción
   (Whisper)
      │
      ▼
 Mejora IA (Opcional)
      │
      ▼
 Generación PDF
      │
      ▼
 Documento Final
```

---

# 📦 Tecnologías Utilizadas

* Python 3.10+
* Whisper
* Groq API
* CustomTkinter
* ReportLab
* FFmpeg

---

# 📂 Formatos Compatibles

### Audio

* MP3
* WAV
* M4A
* OGG
* FLAC
* AAC
* WMA
* OPUS

### Video

* MP4
* MKV
* AVI
* MOV
* WMV
* FLV
* WEBM
* TS
* MTS
* MPG
* MPEG
* 3GP

---

# 🚀 Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/tuusuario/transcriptor-audio.git

cd transcriptor-audio
```

---

## 2. Crear entorno virtual

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Instalar FFmpeg

### Windows

Descargar desde:

[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

Agregar FFmpeg al PATH o seleccionar manualmente el ejecutable desde la aplicación.

### Linux

```bash
sudo apt install ffmpeg
```

### macOS

```bash
brew install ffmpeg
```

---

# 📋 Dependencias Principales

```txt
openai-whisper
groq
customtkinter
reportlab
torch
```

Instalación manual:

```bash
pip install openai-whisper groq customtkinter reportlab torch
```

---

# 🔑 Configuración de Groq (Opcional)

Si deseas mejorar automáticamente las transcripciones:

1. Crear una cuenta en Groq.
2. Obtener una API Key.
3. Ingresarla en la aplicación.
4. Presionar **Guardar**.

La clave quedará almacenada localmente para futuros usos.

---

# 🎯 Modelos Whisper Disponibles

| Modelo | Velocidad  | Calidad   |
| ------ | ---------- | --------- |
| Tiny   | Muy rápida | Baja      |
| Base   | Rápida     | Buena     |
| Small  | Media      | Muy buena |
| Medium | Lenta      | Alta      |

---

# 🖥️ Uso

### 1. Seleccionar un archivo

Puede ser audio o video.

### 2. Ingresar un título

Ejemplo:

```text
Clase 5 - Bases de Datos
```

### 3. Elegir calidad de transcripción

Seleccionar el modelo Whisper deseado.

### 4. Activar mejora con IA (Opcional)

Ingresar la API Key de Groq.

### 5. Presionar

```text
▶ Transcribir y guardar PDF
```

### 6. Guardar el documento generado

La aplicación creará automáticamente el PDF final.

---

# 📄 Ejemplo de PDF Generado

El documento incluye:

* Título de la transcripción
* Fecha y hora de generación
* Nombre del archivo original
* Texto transcrito
* Indicador de mejora con IA
* Diseño profesional para lectura

---

# 📁 Estructura del Proyecto

```text
transcriptor-audio/
│
├── transcriptor_audio.py
├── .groq_key
├── requirements.txt
├── README.md
│
└── assets/
```

---

# 🔒 Privacidad

* Los archivos se procesan localmente mediante Whisper.
* Solo se envía texto a Groq cuando se activa la mejora con IA.
* La API Key se almacena únicamente en el equipo del usuario.

---

# 💡 Casos de Uso

* Clases universitarias
* Reuniones de trabajo
* Entrevistas
* Podcasts
* Conferencias
* Cursos online
* Grabaciones personales
* Creación de apuntes automáticos

---

# 🛠️ Futuras Mejoras

* Exportación a Word (.docx)
* Exportación a Markdown
* Resúmenes automáticos con IA
* Identificación de hablantes
* Traducción automática
* Historial de transcripciones
* Procesamiento por lotes
* Barra de progreso real

---

# 👨‍💻 Autor

Proyecto desarrollado en Python utilizando Whisper, Groq y CustomTkinter para ofrecer una solución moderna de transcripción y generación automática de documentos PDF.

---

## ⭐ Si te resulta útil

Considera darle una estrella al repositorio para apoyar el proyecto.

```bash
⭐ Star this repository
```
