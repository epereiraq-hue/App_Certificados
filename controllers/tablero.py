"""Controlador para la vista del Tablero Principal."""

from flask import Blueprint, render_template
from models.certificados import obtener_resumen_certificados

tablero_bp = Blueprint("tablero", __name__)


@tablero_bp.route("/")
def index():
    """Ruta principal que muestra el tablero de control de certificados."""
    resumen = obtener_resumen_certificados()
    return render_template(
        "tablero.html",
        conteos=resumen["conteos"],
        estudiantes=resumen["estudiantes"],
        inconsistencias=resumen["inconsistencias"]
    )
