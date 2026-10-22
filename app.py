"""Aplicación principal Flask para la gestión de Certificados de la Academia.

Crea la instancia en la variable 'app' y ejecuta el servidor en el puerto 5000.
"""

import os
from pathlib import Path
from flask import Flask, render_template
from controllers.tablero import tablero_bp
from controllers.carga import carga_bp
from controllers.certificados import certificados_bp

# Carpeta raiz del proyecto: donde esta este archivo app.py.
# Asi las rutas funcionan igual sin importar desde donde se ejecute.
BASE_DIR = Path(__file__).resolve().parent
INSUMOS_DIR = BASE_DIR / "Insumos"
RUTA_MAESTRO = INSUMOS_DIR / "Maestro_Estudiantes.xlsx"
RUTA_EVALUACIONES = INSUMOS_DIR / "Registro_Evaluaciones.xlsx"

# LADRILLO: variable tipo bool que dice si estamos en la nube (Vercel).
# Vercel pone la variable de entorno VERCEL=1 automaticamente.
EN_VERCEL = bool(os.environ.get("VERCEL"))

# Los archivos estaticos (CSS) viven en public/static/.
# Vercel sirve public/ tal cual, asi que la URL /static/css/estilos.css
# funciona igual en local y en la nube, sin duplicar archivos.
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "views"),
    static_folder=str(BASE_DIR / "public" / "static"),
)

# Registrar Blueprints
app.register_blueprint(tablero_bp)
app.register_blueprint(carga_bp)
app.register_blueprint(certificados_bp)


# LADRILLO: FUNCION que atrapa los errores 404 y muestra una pagina en espanol.
@app.errorhandler(404)
def pagina_no_encontrada(error):
    mensaje = getattr(error, "description", "La dirección solicitada no existe.")
    return render_template("error404.html", mensaje=mensaje), 404


if __name__ == "__main__":
    # Este bloque SOLO corre en tu computadora (python app.py).
    # En Vercel la app la enciende la plataforma, no este bloque.
    port = int(os.environ.get("PORT", 5000))
    # LADRILLO: CONDICIONAL para decidir el modo depuracion.
    # En local se activa (recarga sola al guardar); se apaga con FLASK_DEBUG=0.
    debug = os.environ.get("FLASK_DEBUG", "0" if EN_VERCEL else "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
