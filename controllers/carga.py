"""Controlador de carga de Excel (capa controllers).

Solo recibe los archivos del formulario y llama al servicio.
La lectura, la limpieza y el guardado viven en services/carga_excel.py.
"""

from flask import Blueprint, render_template, request

from services.carga_excel import cargar_desde_formulario

carga_bp = Blueprint("carga", __name__)


@carga_bp.route("/cargar", methods=["GET", "POST"])
def cargar():
    """Muestra el formulario (GET) y procesa los dos Excel subidos (POST)."""
    # LADRILLO: variables tipo dict o None con el resultado o el error.
    resultado = None
    error = None

    # LADRILLO: CONDICIONAL. Solo se procesa cuando el formulario se envía.
    if request.method == "POST":
        archivo_maestro = request.files.get("maestro")
        archivo_evaluaciones = request.files.get("evaluaciones")

        if (
            archivo_maestro is None
            or archivo_evaluaciones is None
            or not archivo_maestro.filename
            or not archivo_evaluaciones.filename
        ):
            error = "Debes seleccionar los dos archivos Excel."
        else:
            try:
                # LADRILLO: variable tipo tuple (estudiantes guardados, evaluaciones guardadas).
                total_estudiantes, total_evaluaciones = cargar_desde_formulario(
                    archivo_maestro, archivo_evaluaciones
                )
                resultado = {
                    "estudiantes": total_estudiantes,
                    "evaluaciones": total_evaluaciones,
                }
            except ValueError as exc:
                # Errores de columnas o de formato: se muestran al usuario.
                error = str(exc)
            except Exception as exc:  # noqa: BLE001 (queremos ver el detalle en pantalla)
                error = f"No se pudo cargar la información: {exc}"

    return render_template("cargar.html", resultado=resultado, error=error)
