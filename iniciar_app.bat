@echo off
REM Arranca la App de Certificados con doble clic (capa raiz).
cd /d "%~dp0"
echo Cargando datos desde Insumos...
uv run python cargar_datos.py
echo.
echo Abriendo la app en http://localhost:5000 ...
uv run python app.py
pause
