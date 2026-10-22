"""Servicio de generación de certificados en PDF (capa services).

- Usa la librería fpdf2 (sin inteligencia artificial: solo dibuja texto).
- Un certificado por estudiante + programa, en hoja A4 horizontal.
- Colores institucionales: azul marino #14213D y dorado #B8923D.
- También arma el ZIP con todos los certificados de una sola vez.
"""

import io
import re
import unicodedata
import zipfile
from datetime import date
from typing import Any, Dict, List

from fpdf import FPDF

# LADRILLO: constantes de color y medidas (variables que nunca cambian).
AZUL_MARINO = (20, 33, 61)      # #14213D
DORADO = (184, 146, 61)         # #B8923D
GRIS_TEXTO = (108, 117, 125)
ANCHO_PAGINA = 297              # milímetros de una A4 horizontal
ALTO_PAGINA = 210

MESES_EN_ESPANOL = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def _nuevo_pdf() -> FPDF:
    """Crea una hoja A4 horizontal ya configurada con los márgenes del certificado."""
    pdf = FPDF(orientation="landscape", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    return pdf


def _dibujar_marco(pdf: FPDF) -> None:
    """Dibuja el marco doble: línea gruesa azul marino y línea fina dorada."""
    pdf.set_line_width(1.4)
    pdf.set_draw_color(*AZUL_MARINO)
    pdf.rect(8, 8, ANCHO_PAGINA - 16, ALTO_PAGINA - 16)
    pdf.set_line_width(0.5)
    pdf.set_draw_color(*DORADO)
    pdf.rect(12, 12, ANCHO_PAGINA - 24, ALTO_PAGINA - 24)


def _texto_centrado(pdf: FPDF, texto: str, alto: float) -> None:
    """Escribe una línea centrada y baja el cursor (ladrillo: función reutilizable)."""
    pdf.cell(0, alto, texto, align="C", new_x="LMARGIN", new_y="NEXT")


def _fecha_de_hoy_en_espanol() -> str:
    """Devuelve la fecha actual como texto, por ejemplo: 21 de octubre de 2026."""
    hoy = date.today()
    return f"{hoy.day} de {MESES_EN_ESPANOL[hoy.month - 1]} de {hoy.year}"


def _sin_acentos(texto: str) -> str:
    """Quita tildes y símbolos raros para que el nombre del archivo sea seguro."""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^A-Za-z0-9]+", "_", texto).strip("_")
    return texto


def nombre_archivo_certificado(estudiante: Dict[str, Any]) -> str:
    """Arma el nombre del PDF: 101230456_Camila_Rojas_Mendez.pdf."""
    identificacion = str(estudiante.get("identificacion", "")).strip()
    nombre = _sin_acentos(estudiante.get("nombre_completo", "estudiante"))
    return f"{identificacion}_{nombre}.pdf"


def generar_certificado_pdf(estudiante: Dict[str, Any]) -> bytes:
    """Genera UN certificado en PDF y lo devuelve como bytes (para enviarlo al navegador).

    'estudiante' es un diccionario que viene del modelo con:
    nombre_completo, programa, cohorte, modulos, promedio_nota,
    promedio_asistencia y estado_certificado.
    """
    pdf = _nuevo_pdf()
    _dibujar_marco(pdf)

    # LADRILLO: variable tipo str con el tipo que decidió el modelo (R3/R4).
    tipo = str(estudiante.get("estado_certificado", "")).strip()

    pdf.set_y(26)
    # Encabezado institucional.
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*AZUL_MARINO)
    _texto_centrado(pdf, "ACADEMIA HORIZONTE", 10)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*DORADO)
    _texto_centrado(pdf, "FORMACIÓN TÉCNICA PARA EMPRESAS", 6)

    pdf.ln(6)
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(*GRIS_TEXTO)
    _texto_centrado(pdf, "otorga el presente", 8)

    # Título grande y dorado.
    pdf.set_font("Helvetica", "B", 30)
    pdf.set_text_color(*AZUL_MARINO)
    _texto_centrado(pdf, f"CERTIFICADO DE {tipo.upper()}", 15)

    pdf.ln(2)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(*GRIS_TEXTO)
    _texto_centrado(pdf, "a", 6)

    # Nombre del estudiante con una línea dorada debajo.
    nombre = str(estudiante.get("nombre_completo", "")).strip()
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*AZUL_MARINO)
    ancho_nombre = pdf.get_string_width(nombre)
    _texto_centrado(pdf, nombre, 12)
    x_inicio = (ANCHO_PAGINA - ancho_nombre) / 2
    y_linea = pdf.get_y() + 1
    pdf.set_draw_color(*DORADO)
    pdf.set_line_width(0.8)
    pdf.line(x_inicio, y_linea, x_inicio + ancho_nombre, y_linea)

    pdf.ln(6)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*GRIS_TEXTO)
    _texto_centrado(pdf, "por haber culminado el programa", 6)

    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(*AZUL_MARINO)
    _texto_centrado(pdf, str(estudiante.get("programa", "")).strip(), 9)

    # LADRILLO: variable tipo str con la cohorte (si viene vacía no se muestra).
    cohorte = str(estudiante.get("cohorte", "")).strip()
    if cohorte:
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*GRIS_TEXTO)
        _texto_centrado(pdf, f"Cohorte {cohorte}", 6)

    # Fila de resultados: promedio, asistencia y módulos.
    pdf.ln(4)
    promedio = float(estudiante.get("promedio_nota", 0))
    asistencia = float(estudiante.get("promedio_asistencia", 0))
    modulos = int(estudiante.get("modulos", 0))
    _fila_resultados(pdf, promedio, asistencia, modulos)

    # Pie: fecha de emisión y firma.
    pdf.set_y(ALTO_PAGINA - 46)
    pdf.set_draw_color(*DORADO)
    pdf.set_line_width(0.4)
    pdf.line((ANCHO_PAGINA / 2) - 45, pdf.get_y(), (ANCHO_PAGINA / 2) + 45, pdf.get_y())
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*AZUL_MARINO)
    _texto_centrado(pdf, "Coordinación Académica", 5)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*GRIS_TEXTO)
    _texto_centrado(pdf, f"Emitido el {_fecha_de_hoy_en_espanol()}", 5)

    # fpdf2 devuelve bytearray: lo pasamos a bytes puros.
    return bytes(pdf.output())


def _fila_resultados(pdf: FPDF, promedio: float, asistencia: float, modulos: int) -> None:
    """Dibuja tres casillas centradas con promedio, asistencia y módulos."""
    datos = [
        ("PROMEDIO", f"{promedio:.2f}"),
        ("ASISTENCIA", f"{asistencia:.2f}%"),
        ("MÓDULOS", str(modulos)),
    ]
    ancho_caja = 50
    separacion = 8
    ancho_total = len(datos) * ancho_caja + (len(datos) - 1) * separacion
    x = (ANCHO_PAGINA - ancho_total) / 2
    y = pdf.get_y()

    for titulo, valor in datos:
        pdf.set_draw_color(*AZUL_MARINO)
        pdf.set_line_width(0.4)
        pdf.rect(x, y, ancho_caja, 20)
        pdf.set_xy(x, y + 3)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*AZUL_MARINO)
        pdf.cell(ancho_caja, 8, valor, align="C")
        pdf.set_xy(x, y + 11)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*GRIS_TEXTO)
        pdf.cell(ancho_caja, 6, titulo, align="C")
        x += ancho_caja + separacion

    pdf.set_y(y + 24)


def generar_zip_certificados(estudiantes: List[Dict[str, Any]]) -> bytes:
    """Genera un ZIP en memoria con un PDF por cada estudiante de la lista."""
    buffer = io.BytesIO()
    # LADRILLO: BUCLE que crea un PDF por estudiante y lo mete dentro del ZIP.
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archivo_zip:
        for estudiante in estudiantes:
            pdf_bytes = generar_certificado_pdf(estudiante)
            archivo_zip.writestr(nombre_archivo_certificado(estudiante), pdf_bytes)
    return buffer.getvalue()
