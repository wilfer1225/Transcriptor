import os
import subprocess
import threading
import datetime
import json
import whisper
import customtkinter as ctk
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import tempfile

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_BG      = "#0f0f0f"
COLOR_CARD    = "#1a1a1a"
COLOR_CARD2   = "#222222"
COLOR_ACCENT  = "#c9a84c"
COLOR_ACCENT2 = "#e8c97a"
COLOR_TEXT    = "#f0ece0"
COLOR_SUBTEXT = "#888888"
COLOR_SUCCESS = "#4caf7d"
COLOR_ERROR   = "#e05c5c"
COLOR_BORDER  = "#2a2a2a"
FONT_TITLE    = ("Georgia", 22, "bold")
FONT_LABEL    = ("Segoe UI", 11)
FONT_SMALL    = ("Segoe UI", 10)
FONT_MONO     = ("Consolas", 10)

KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".groq_key")

def cargar_api_key() -> str:
    if os.path.isfile(KEY_FILE):
        with open(KEY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def guardar_api_key(key: str):
    with open(KEY_FILE, "w", encoding="utf-8") as f:
        f.write(key.strip())

def mejorar_con_groq(texto: str, titulo: str, api_key: str) -> str:
    """Envía la transcripción a Groq y devuelve el texto mejorado."""
    from groq import Groq

    cliente = Groq(api_key=api_key)

    prompt = f"""Eres un asistente experto en corrección y estructuración de transcripciones de audio.

El siguiente texto es una transcripción automática (puede tener errores de puntuación, palabras mal transcritas, frases cortadas, repeticiones, etc).

El contexto/tema de la transcripción es: "{titulo}"

Tu tarea:
1. Corregí errores ortográficos y de puntuación
2. Separá el texto en párrafos con sentido lógico
3. Corregí palabras que claramente fueron mal transcritas según el contexto
4. Mantené el contenido original — no agregues ni inventes información
5. Devolvé SOLO el texto corregido, sin explicaciones ni comentarios

Transcripción original:
{texto}"""

    respuesta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4096,
    )

    return respuesta.choices[0].message.content.strip()

def generar_pdf(titulo: str, texto: str, ruta_salida: str,
                nombre_archivo: str, mejorado_con_ia: bool = False):
    doc = SimpleDocTemplate(
        ruta_salida, pagesize=A4,
        rightMargin=2.5*cm, leftMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
        title=titulo, author="Transcriptor de Audio",
    )

    GOLD = colors.HexColor("#c9a84c")
    DARK = colors.HexColor("#1a1a1a")
    GREY = colors.HexColor("#666666")
    BLUE = colors.HexColor("#5b9bd5")

    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "Titulo", parent=styles["Title"],
        fontName="Times-Bold", fontSize=26, leading=32,
        textColor=GOLD, alignment=TA_CENTER, spaceAfter=6,
    )
    estilo_meta = ParagraphStyle(
        "Meta", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10, leading=14,
        textColor=GREY, alignment=TA_CENTER, spaceAfter=4,
    )
    estilo_badge = ParagraphStyle(
        "Badge", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=9, leading=13,
        textColor=BLUE, alignment=TA_CENTER, spaceAfter=4,
    )
    estilo_cuerpo = ParagraphStyle(
        "Cuerpo", parent=styles["Normal"],
        fontName="Times-Roman", fontSize=12, leading=20,
        textColor=DARK, alignment=TA_JUSTIFY,
        spaceAfter=12, firstLineIndent=18,
    )

    story = []
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(titulo, estilo_titulo))
    story.append(Spacer(1, 0.2*cm))

    fecha = datetime.datetime.now().strftime("%d de %B de %Y · %H:%M hs")
    story.append(Paragraph(f"Transcripción generada el {fecha}", estilo_meta))
    story.append(Paragraph(f"Archivo original: {nombre_archivo}", estilo_meta))

    if mejorado_con_ia:
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph("✦ Texto mejorado con IA (Groq · LLaMA 3.3 70B)", estilo_badge))

    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceAfter=20))

    for parrafo in [p.strip() for p in texto.split("\n") if p.strip()]:
        story.append(Paragraph(parrafo, estilo_cuerpo))

    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GREY))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Generado con Transcriptor de Audio · Whisper + Groq", estilo_meta))

    doc.build(story)

_FFMPEG_PATH: str | None = None

def buscar_ffmpeg() -> str:
    global _FFMPEG_PATH
    if _FFMPEG_PATH:
        return _FFMPEG_PATH
    for cmd in ("ffmpeg", "ffmpeg.exe"):
        try:
            subprocess.run([cmd, "-version"], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, check=True)
            _FFMPEG_PATH = cmd
            return cmd
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    userprofile = os.environ.get("USERPROFILE", "")
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    rutas = [
        r"C:\ffmpeg\bin\ffmpeg.exe", r"C:\ffmpeg\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        os.path.join(userprofile, "ffmpeg", "bin", "ffmpeg.exe"),
        os.path.join(script_dir, "ffmpeg.exe"),
        os.path.join(script_dir, "ffmpeg", "bin", "ffmpeg.exe"),
    ]
    for ruta in rutas:
        if os.path.isfile(ruta):
            _FFMPEG_PATH = ruta
            return ruta
    raise FileNotFoundError("FFMPEG_NO_ENCONTRADO")

def convertir_a_wav(ruta_origen: str) -> str:
    ffmpeg = buscar_ffmpeg()
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    cmd = [ffmpeg, "-y", "-i", ruta_origen, "-ar", "16000", "-ac", "1", "-f", "wav", tmp.name]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        err = res.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"FFmpeg error:\n{err[-600:]}")
    return tmp.name

class TranscriptorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Transcriptor de Audio")
        self.geometry("860x780")
        self.minsize(720, 640)
        self.configure(fg_color=COLOR_BG)

        self.ruta_audio     = None
        self.modelo_whisper = None
        self.modelo_cargado = False
        self._texto_crudo   = ""

        self._construir_ui()
        self._cargar_modelo_en_hilo()
        self._verificar_ffmpeg()

    def _construir_ui(self):
        header = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=0, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="✦  Transcriptor de Audio",
                     font=FONT_TITLE, text_color=COLOR_ACCENT
                     ).pack(side="left", padx=28, pady=18)

        self.lbl_ffmpeg = ctk.CTkLabel(header, text="⏳ FFmpeg…",
                                        font=FONT_SMALL, text_color=COLOR_SUBTEXT, cursor="hand2")
        self.lbl_ffmpeg.pack(side="right", padx=8)
        self.lbl_ffmpeg.bind("<Button-1>", lambda e: self._seleccionar_ffmpeg_manual())

        self.lbl_modelo = ctk.CTkLabel(header, text="⏳ Cargando modelo…",
                                        font=FONT_SMALL, text_color=COLOR_SUBTEXT)
        self.lbl_modelo.pack(side="right", padx=8)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=16)

        self._label(body, "1 · Seleccionar audio o video")
        fila = ctk.CTkFrame(body, fg_color="transparent")
        fila.pack(fill="x", pady=(4, 10))
        self.lbl_archivo = ctk.CTkLabel(fila, text="Ningún archivo seleccionado",
                                         font=FONT_SMALL, text_color=COLOR_SUBTEXT, anchor="w")
        self.lbl_archivo.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(fila, text="Elegir archivo", width=140, height=36,
                      font=FONT_LABEL, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT2,
                      text_color="#0f0f0f", corner_radius=8,
                      command=self._seleccionar_audio).pack(side="right")

        self._label(body, "2 · Título de la transcripción")
        self.entry_titulo = ctk.CTkEntry(body, placeholder_text="Ej: Clase 3 Economía",
                                          font=FONT_LABEL, height=40, corner_radius=8,
                                          border_color=COLOR_BORDER, fg_color=COLOR_CARD,
                                          text_color=COLOR_TEXT)
        self.entry_titulo.pack(fill="x", pady=(4, 10))

        self._label(body, "3 · Calidad de transcripción (Whisper)")
        fila_m = ctk.CTkFrame(body, fg_color="transparent")
        fila_m.pack(fill="x", pady=(4, 10))
        ctk.CTkLabel(fila_m, text="Modelo:", font=FONT_SMALL, text_color=COLOR_SUBTEXT).pack(side="left")
        self.combo_modelo = ctk.CTkComboBox(
            fila_m,
            values=["tiny (rápido)", "base (balanceado)", "small (mejor calidad)", "medium (alta calidad)"],
            width=220, font=FONT_SMALL, fg_color=COLOR_CARD, border_color=COLOR_BORDER,
            button_color=COLOR_ACCENT, dropdown_fg_color=COLOR_CARD, text_color=COLOR_TEXT,
        )
        self.combo_modelo.set("base (balanceado)")
        self.combo_modelo.pack(side="left", padx=10)

        self._label(body, "4 · Mejora con IA (Groq — opcional)")
        frame_ia = ctk.CTkFrame(body, fg_color=COLOR_CARD2, corner_radius=8)
        frame_ia.pack(fill="x", pady=(4, 10))

        fila_ia = ctk.CTkFrame(frame_ia, fg_color="transparent")
        fila_ia.pack(fill="x", padx=12, pady=10)

        self.switch_ia = ctk.CTkSwitch(
            fila_ia, text="Activar mejora con IA",
            font=FONT_LABEL, text_color=COLOR_TEXT,
            progress_color=COLOR_ACCENT, button_color=COLOR_ACCENT2,
            command=self._toggle_ia,
        )
        self.switch_ia.pack(side="left")

        self.lbl_ia_estado = ctk.CTkLabel(fila_ia, text="", font=FONT_SMALL, text_color=COLOR_SUBTEXT)
        self.lbl_ia_estado.pack(side="right")

        fila_key = ctk.CTkFrame(frame_ia, fg_color="transparent")
        fila_key.pack(fill="x", padx=12, pady=(0, 10))

        ctk.CTkLabel(fila_key, text="API Key Groq:", font=FONT_SMALL,
                     text_color=COLOR_SUBTEXT, width=90, anchor="w").pack(side="left")

        self.entry_key = ctk.CTkEntry(
            fila_key, placeholder_text="gsk_...",
            font=FONT_MONO, height=34, corner_radius=6,
            border_color=COLOR_BORDER, fg_color=COLOR_CARD,
            text_color=COLOR_TEXT, show="•",
        )
        self.entry_key.pack(side="left", fill="x", expand=True, padx=(6, 6))

        key_guardada = cargar_api_key()
        if key_guardada:
            self.entry_key.insert(0, key_guardada)
            self.lbl_ia_estado.configure(text="Key guardada ✓", text_color=COLOR_SUCCESS)

        ctk.CTkButton(fila_key, text="Guardar", width=80, height=34,
                      font=FONT_SMALL, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT2,
                      text_color="#0f0f0f", corner_radius=6,
                      command=self._guardar_key).pack(side="right")

        self.btn_transcribir = ctk.CTkButton(
            body, text="▶  Transcribir y guardar PDF",
            font=("Segoe UI", 13, "bold"), height=48, corner_radius=10,
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT2, text_color="#0f0f0f",
            command=self._iniciar_transcripcion,
        )
        self.btn_transcribir.pack(fill="x", pady=(6, 12))

        self.barra_estado = ctk.CTkProgressBar(body, mode="indeterminate", height=4,
                                                fg_color=COLOR_BORDER, progress_color=COLOR_ACCENT)
        self.barra_estado.pack(fill="x", pady=(0, 6))
        self.barra_estado.set(0)

        self.lbl_estado = ctk.CTkLabel(body, text="Listo", font=FONT_SMALL, text_color=COLOR_SUBTEXT)
        self.lbl_estado.pack(anchor="w")

        self._label(body, "Vista previa")
        self.texto_preview = ctk.CTkTextbox(
            body, font=FONT_MONO, fg_color=COLOR_CARD, text_color=COLOR_TEXT,
            corner_radius=8, border_color=COLOR_BORDER, border_width=1,
            height=150, wrap="word", state="disabled",
        )
        self.texto_preview.pack(fill="both", expand=True, pady=(4, 0))

    def _label(self, parent, texto):
        ctk.CTkLabel(parent, text=texto, font=("Segoe UI", 11, "bold"),
                     text_color=COLOR_ACCENT, anchor="w").pack(anchor="w", pady=(6, 0))

    def _toggle_ia(self):
        if self.switch_ia.get():
            key = self.entry_key.get().strip()
            if not key:
                messagebox.showwarning("Sin API Key",
                    "Ingresá tu API Key de Groq.\n\nObtené una gratis en: console.groq.com")
                self.switch_ia.deselect()

    def _guardar_key(self):
        key = self.entry_key.get().strip()
        if not key:
            messagebox.showwarning("Vacío", "Ingresá una API Key antes de guardar.")
            return
        guardar_api_key(key)
        self.lbl_ia_estado.configure(text="Key guardada ✓", text_color=COLOR_SUCCESS)
        messagebox.showinfo("Guardado", "API Key guardada correctamente.\nSe cargará automáticamente la próxima vez.")

    def _verificar_ffmpeg(self):
        def _check():
            try:
                buscar_ffmpeg()
                self.after(0, lambda: self.lbl_ffmpeg.configure(
                    text="✓ FFmpeg", text_color=COLOR_SUCCESS))
            except FileNotFoundError:
                self.after(0, self._mostrar_aviso_ffmpeg)
        threading.Thread(target=_check, daemon=True).start()

    def _mostrar_aviso_ffmpeg(self):
        self.lbl_ffmpeg.configure(text="⚠ FFmpeg no encontrado", text_color=COLOR_ERROR)
        if messagebox.askyesno("FFmpeg no encontrado",
            "FFmpeg es necesario para convertir los archivos.\n\n"
            "¿Querés buscarlo manualmente ahora?"):
            self._seleccionar_ffmpeg_manual()

    def _seleccionar_ffmpeg_manual(self):
        ruta = filedialog.askopenfilename(
            title="Seleccioná ffmpeg.exe",
            filetypes=[("FFmpeg", "ffmpeg.exe ffmpeg"), ("Ejecutables", "*.exe"), ("Todos", "*.*")],
        )
        if ruta and os.path.isfile(ruta):
            import transcriptor_audio as _mod
            _mod._FFMPEG_PATH = ruta
            self.lbl_ffmpeg.configure(text="✓ FFmpeg", text_color=COLOR_SUCCESS)
            messagebox.showinfo("FFmpeg configurado", f"Usando:\n{ruta}")

    def _cargar_modelo_en_hilo(self):
        def _cargar():
            try:
                self.modelo_whisper = whisper.load_model(self._nombre_modelo())
                self.modelo_cargado = True
                self.after(0, lambda: self.lbl_modelo.configure(
                    text="✓ Modelo listo", text_color=COLOR_SUCCESS))
            except Exception:
                self.after(0, lambda: self.lbl_modelo.configure(
                    text="✗ Error modelo", text_color=COLOR_ERROR))
        threading.Thread(target=_cargar, daemon=True).start()

    def _nombre_modelo(self) -> str:
        return self.combo_modelo.get().split(" ")[0]

    def _seleccionar_audio(self):
        tipos = [
            ("Todos los formatos",
             "*.mp3 *.wav *.m4a *.ogg *.flac *.aac *.wma *.opus "
             "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.ts *.mts "
             "*.m2ts *.3gp *.3g2 *.vob *.mpg *.mpeg *.ogv"),
            ("Solo audio", "*.mp3 *.wav *.m4a *.ogg *.flac *.aac *.wma *.opus *.webm"),
            ("Solo video", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.ts *.3gp *.mpg *.mpeg"),
            ("Todos los archivos", "*.*"),
        ]
        ruta = filedialog.askopenfilename(title="Seleccionar audio o video", filetypes=tipos)
        if ruta:
            self.ruta_audio = ruta
            self.lbl_archivo.configure(text=f"📁 {os.path.basename(ruta)}", text_color=COLOR_TEXT)

    def _iniciar_transcripcion(self):
        if not self.ruta_audio:
            messagebox.showwarning("Sin audio", "Por favor seleccioná un archivo de audio o video.")
            return
        if not self.entry_titulo.get().strip():
            messagebox.showwarning("Sin título", "Por favor ingresá un título para la transcripción.")
            return
        if not self.modelo_cargado:
            messagebox.showinfo("Espera", "El modelo aún está cargando. Intentá en unos segundos.")
            return
        if self.switch_ia.get() and not self.entry_key.get().strip():
            messagebox.showwarning("Sin API Key", "Ingresá tu API Key de Groq para usar la mejora con IA.")
            return

        nombre_modelo = self._nombre_modelo()
        mels_actual   = self.modelo_whisper.dims.n_mels
        mels_nuevo    = 128 if nombre_modelo == "large" else 80

        if mels_actual != mels_nuevo:
            self._set_estado("Cargando nuevo modelo…", COLOR_ACCENT)
            self.modelo_cargado = False
            self.lbl_modelo.configure(text="⏳ Cargando…", text_color=COLOR_SUBTEXT)
            def recargar():
                self.modelo_whisper = whisper.load_model(nombre_modelo)
                self.modelo_cargado = True
                self.after(0, lambda: self.lbl_modelo.configure(text="✓ Modelo listo", text_color=COLOR_SUCCESS))
                self.after(0, self._transcribir)
            threading.Thread(target=recargar, daemon=True).start()
        else:
            self._transcribir()

    def _transcribir(self):
        self.btn_transcribir.configure(state="disabled")
        self.barra_estado.start()

        titulo      = self.entry_titulo.get().strip()
        ruta_audio  = self.ruta_audio
        nombre_orig = os.path.basename(ruta_audio)
        usar_ia     = bool(self.switch_ia.get())
        api_key     = self.entry_key.get().strip()

        def _hilo():
            try:
                self.after(0, lambda: self._set_estado("Convirtiendo audio…", COLOR_ACCENT))
                wav_tmp = convertir_a_wav(ruta_audio)

                self.after(0, lambda: self._set_estado("Transcribiendo con Whisper…", COLOR_ACCENT))
                resultado = self.modelo_whisper.transcribe(wav_tmp, fp16=False)
                texto = resultado["text"].strip()
                os.unlink(wav_tmp)

                texto_final    = texto
                mejorado_con_ia = False

                if usar_ia and api_key:
                    self.after(0, lambda: self._set_estado("Mejorando texto con IA (Groq)…", COLOR_ACCENT))
                    try:
                        texto_final     = mejorar_con_groq(texto, titulo, api_key)
                        mejorado_con_ia = True
                    except Exception as e_ia:
                        msg_ia = str(e_ia)
                        self.after(0, lambda m=msg_ia: messagebox.showwarning(
                            "IA no disponible",
                            f"No se pudo mejorar con IA (se guardará la transcripción original):\n{m}"
                        ))

                nombre_pdf = titulo.replace(" ", "_") + ".pdf"
                self.after(0, lambda: self._guardar_pdf(
                    titulo, texto_final, nombre_pdf, nombre_orig, mejorado_con_ia, texto
                ))

            except Exception as e:
                msg = str(e)
                self.after(0, lambda m=msg: self._on_error(m))

        threading.Thread(target=_hilo, daemon=True).start()

    def _guardar_pdf(self, titulo, texto, nombre_sugerido, nombre_orig, mejorado, texto_crudo):
        self.barra_estado.stop()
        self.barra_estado.set(0)

        ruta_pdf = filedialog.asksaveasfilename(
            defaultextension=".pdf", initialfile=nombre_sugerido,
            filetypes=[("PDF", "*.pdf")], title="Guardar PDF",
        )
        if not ruta_pdf:
            self._set_estado("Guardado cancelado.", COLOR_SUBTEXT)
            self.btn_transcribir.configure(state="normal")
            return

        try:
            generar_pdf(titulo, texto, ruta_pdf, nombre_orig, mejorado_con_ia=mejorado)
            self._set_estado(f"✓ PDF guardado: {os.path.basename(ruta_pdf)}", COLOR_SUCCESS)

            self.texto_preview.configure(state="normal")
            self.texto_preview.delete("1.0", "end")
            if mejorado and texto != texto_crudo:
                self.texto_preview.insert("end", "── TEXTO MEJORADO CON IA ──\n\n")
                self.texto_preview.insert("end", texto)
                self.texto_preview.insert("end", "\n\n── TRANSCRIPCIÓN ORIGINAL ──\n\n")
                self.texto_preview.insert("end", texto_crudo)
            else:
                self.texto_preview.insert("end", texto)
            self.texto_preview.configure(state="disabled")

            messagebox.showinfo("¡Listo!", f"Transcripción guardada exitosamente:\n{ruta_pdf}")
        except Exception as e:
            self._on_error(str(e))
        finally:
            self.btn_transcribir.configure(state="normal")

    def _on_error(self, msg):
        self.barra_estado.stop()
        self.barra_estado.set(0)
        self.btn_transcribir.configure(state="normal")
        self._set_estado(f"✗ Error: {msg}", COLOR_ERROR)
        messagebox.showerror("Error", f"Ocurrió un error:\n\n{msg}")

    def _set_estado(self, msg, color=None):
        self.lbl_estado.configure(text=msg, text_color=color or COLOR_SUBTEXT)

if __name__ == "__main__":
    app = TranscriptorApp()
    app.mainloop()