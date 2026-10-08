"""Aplicación principal Flask para la gestión de Certificados de la Academia.

Crea la instancia en la variable 'app' y ejecuta el servidor en el puerto 5000.
"""

import os
from flask import Flask
from controllers.tablero import tablero_bp

app = Flask(
    __name__,
    template_folder="views",
    static_folder="static"
)

# Registrar Blueprints
app.register_blueprint(tablero_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
