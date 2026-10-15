"""Aplicación principal Flask para la gestión de Certificados de la Academia.

Crea la instancia en la variable 'app' y ejecuta el servidor en el puerto 5000.
"""

import os
from pathlib import Path
from flask import Flask
from controllers.tablero import tablero_bp

# Carpeta raiz del proyecto: donde esta este archivo app.py.
# Asi las rutas funcionan igual sin importar desde donde se ejecute.
BASE_DIR = Path(__file__).resolve().parent
INSUMOS_DIR = BASE_DIR / "Insumos"
RUTA_MAESTRO = INSUMOS_DIR / "Maestro_Estudiantes.xlsx"
RUTA_EVALUACIONES = INSUMOS_DIR / "Registro_Evaluaciones.xlsx"

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "views"),
    static_folder=str(BASE_DIR / "static")
)

# Registrar Blueprints
app.register_blueprint(tablero_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
