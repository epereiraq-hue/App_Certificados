"""Controlador para la vista del Tablero Principal (capa controllers)."""

# LADRILLO: variables y tipos llegan del modelo, aqui no se calcula.
from flask import Blueprint, render_template, request
from models.certificados import obtener_resumen_certificados

tablero_bp = Blueprint("tablero", __name__)


@tablero_bp.route("/")
def index():
    """Ruta principal que muestra el tablero (solo pide datos y los pasa a la vista)."""
    # LADRILLO: variable tipo dict con conteos, estudiantes e inconsistencias.
    resumen = obtener_resumen_certificados()
    # LADRILLO: variable tipo str (filtro que viene de la pagina, ?programa=...).
    programa_sel = request.args.get("programa", "todos")
    # LADRILLO: variable tipo list (los dos programas del maestro).
    programas = sorted({e["programa"] for e in resumen["estudiantes"]})
    # LADRILLO: CONDICIONAL + BUCLE para filtrar sin calcular nada.
    if programa_sel == "todos":
        filtrados = resumen["estudiantes"]
    else:
        filtrados = [e for e in resumen["estudiantes"] if e["programa"] == programa_sel]
    return render_template(
        "tablero.html",
        conteos=resumen["conteos"],
        estudiantes=filtrados,
        inconsistencias=resumen["inconsistencias"],
        programas=programas,
        programa_sel=programa_sel,
    )
