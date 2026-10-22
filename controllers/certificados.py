"""Controlador de certificados: un PDF individual y el ZIP con todos (capa controllers).

Aquí NO se calcula nada: se piden los datos al modelo y el PDF al servicio.
"""

from io import BytesIO

from flask import Blueprint, abort, send_file
from werkzeug.utils import secure_filename

from models.certificados import buscar_estudiante, es_certificable, obtener_certificados
from services.generador_pdf import (
    generar_certificado_pdf,
    generar_zip_certificados,
    nombre_archivo_certificado,
)

certificados_bp = Blueprint("certificados", __name__)


@certificados_bp.route("/certificado/<identificacion>/<path:programa>")
def certificado(identificacion: str, programa: str):
    """Descarga el PDF de un estudiante en un programa (Ruta de la Etapa 4)."""
    # LADRILLO: variable tipo dict o None (el estudiante que pidió el navegador).
    estudiante = buscar_estudiante(identificacion, programa)
    # LADRILLO: CONDICIONAL. Si no existe o no lleva certificado, error 404.
    if estudiante is None or not es_certificable(estudiante):
        abort(404, description="No hay certificado para esa identificación y programa.")

    # LADRILLO: variable tipo bytes con el PDF ya fabricado por el servicio.
    pdf_bytes = generar_certificado_pdf(estudiante)
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=nombre_archivo_certificado(estudiante),
    )


@certificados_bp.route("/descargar-todos")
def descargar_todos():
    """Descarga un ZIP con los 22 certificados (19 Aprobación + 3 Participación)."""
    # LADRILLO: variable tipo list con los estudiantes que sí llevan certificado.
    estudiantes = obtener_certificados()
    if not estudiantes:
        abort(404, description="Todavía no hay certificados para descargar.")

    # LADRILLO: variable tipo bytes con el ZIP completo.
    zip_bytes = generar_zip_certificados(estudiantes)
    return send_file(
        BytesIO(zip_bytes),
        mimetype="application/zip",
        as_attachment=True,
        download_name=secure_filename("certificados_academia.zip"),
    )
