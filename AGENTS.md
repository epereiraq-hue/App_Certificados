# App de Certificados de la Academia

## Problema
La Academia emite certificados cruzando a mano dos Excel. Queremos una app web que lea los datos, los guarde en una base de datos, aplique las reglas, genere los certificados en PDF y muestre las inconsistencias. La app NO usa inteligencia artificial: son reglas fijas en Python.

## Datos (insumos/, solo lectura)
- insumos/Maestro_Estudiantes.xlsx, hoja Estudiantes: Identificacion, Nombre_Completo, Correo, Programa, Cohorte (24 filas).
- insumos/Registro_Evaluaciones.xlsx, hoja Evaluaciones: Identificacion, Programa, Modulo, Nota, Asistencia_Pct, Fecha_Cierre (88 filas).
- La Identificacion siempre se trata como texto, sin espacios.

## Base de datos (Supabase, PostgreSQL)
- Tabla estudiantes: identificacion (texto, llave primaria), nombre_completo, correo, programa, cohorte.
- Tabla evaluaciones: id (autonumérico), identificacion, programa, modulo, nota, asistencia_pct, fecha_cierre.
- La conexión se lee de la variable DATABASE_URL del archivo .env (con python-dotenv). Usar psycopg con prepare_threshold=None (Supabase usa un pooler).

## Reglas del negocio
- R1. Agrupar por identificacion + programa.
- R2. Promedio = promedio de nota. Asistencia = promedio de asistencia_pct. Redondear a 2 decimales.
- R3. Aprobación: promedio >= 70 y asistencia >= 80 (los límites incluyen).
- R4. Participación: promedio < 70 y asistencia >= 80.
- R5. Sin certificado: asistencia < 80.
- R6. Inconsistencias (no se certifican, se muestran como alerta): estudiante del maestro sin evaluaciones; identificación con evaluaciones que no está en el maestro; asistencia menor a 50 %.

## Cifras de control (la app solo está terminada si salen)
- 19 Aprobación, 3 Participación, 1 Sin certificado y 3 inconsistencias.
- Inconsistencias esperadas: 304560321 (Javier Espinoza, sin evaluaciones), 999880777 (no está en el maestro), Fernanda Zúñiga (asistencia 36.25).
- Controles: Camila Rojas Méndez 101230456 = 91.25 / 96.25 Aprobación; Luis Acuña Blanco = 72.0 / 81.67 Aprobación.

## Arquitectura (MVC, respetarla siempre)
- Python 3.12 con uv (nunca pip). Librerías: flask, pandas, openpyxl, fpdf2, psycopg[binary], python-dotenv.
- models/datos.py: único archivo que habla con Supabase.
- models/certificados.py: reglas del negocio (constantes NOTA_MINIMA = 70, ASISTENCIA_MINIMA = 80).
- services/carga_excel.py: leer los Excel y guardarlos en Supabase.
- services/generador_pdf.py: certificado en PDF con fpdf2 (A4 horizontal).
- controllers/: rutas de Flask. No calculan: llaman al modelo y a los servicios.
- views/: plantillas HTML (Jinja). Solo muestran. Estilo profesional azul marino (#14213D) y dorado (#B8923D).
- app.py: crea la app Flask en la variable app y la enciende en el puerto 5000.
- Rutas: / (tablero), /cargar (formulario para subir los 2 Excel), /certificado/<identificacion>/<programa> (PDF), /descargar-todos (.zip).

## Cómo trabajar conmigo
- Responde en español, con lenguaje sencillo: soy principiante.
- Antes de construir, muestra un plan corto y espera mi aprobación.
- Trabaja por entregas pequeñas y dime qué archivos cambiaste y en qué capa están.
- Nunca modifiques insumos/. Nunca leas ni muestres el archivo .env. Nunca escribas contraseñas en el código.
- Al cerrar cada entrega: el subagente tester-datos prueba y el subagente revisor revisa.

## Contexto del proyecto
Somos Academia Horizonte, un centro de formación que imparte
programas técnicos a empresas. Al cerrar cada cohorte emitimos
certificados por estudiante. Hoy el proceso es manual en Excel
y Word; vamos a automatizarlo como una APLICACIÓN WEB.

## Arquitectura (3 piezas)
- Bodega (datos): los Excel en insumos/. NO se modifican.
- Cocina (backend): Python con Flask, en app.py.
  Toda la lógica va aquí, NUNCA en la interfaz.
- Salón (frontend): páginas web HTML servidas por Flask.
  Solo muestra información; no calcula ni decide.

## Archivos de entrada
- insumos/Maestro_Estudiantes.xlsx: lista oficial de estudiantes
  (Identificacion, Nombre_Completo, Correo, Programa, Cohorte).
- insumos/Registro_Evaluaciones.xlsx: notas (0-100) y asistencia
  por módulo (Identificacion, Programa, Modulo, Nota,
  Asistencia_Pct, Fecha_Cierre).

## Reglas de negocio
IMPORTANTE: Promedio = suma de Notas / cantidad de módulos cursados.
Asistencia = promedio de Asistencia_Pct.
IMPORTANTE: Se agrupa por Identificacion + Programa. Un certificado
por estudiante y programa.
IMPORTANTE: Aprobación si Promedio >= 70 y Asistencia >= 80.
Participación si Promedio < 70 y Asistencia >= 80.
Sin certificado si Asistencia < 80. Los límites INCLUYEN el valor.

## Estilo de trabajo
- Código simple y comentado en español, señalando dónde están
  los ladrillos: variables, tipos, condicionales, bucles y funciones.
- Diseño web en azul marino y dorado.
- Explícame en español sencillo lo que vayas haciendo.

## Decisiones técnicas (2026-10-14, modo Plan, sin código aún)
- Excel: pandas + openpyxl. pandas agrupa y promedia (88 filas);
  openpyxl es el motor que lee el .xlsx. Se descartó openpyxl solo
  (tocaría promediar a mano) y xlrd (viejo, falla con .xlsx).
- Web: Flask con Jinja en views/. Simple para principiantes.
  Se descartó Django (muy grande) y FastAPI (para APIs, no HTML).
- PDF: fpdf2, A4 horizontal. Se descartó reportlab/weasyprint (más complejos).
- BD: Supabase PostgreSQL con psycopg[binary] (prepare_threshold=None
  por el pooler) + python-dotenv para DATABASE_URL. Solo models/datos.py habla con la BD.
- Estructura que respetaremos: app.py (puerto 5000) / controllers/ (rutas, no calculan)
  / models/datos.py + models/certificados.py (NOTA_MINIMA=70, ASISTENCIA_MINIMA=80)
  / services/carga_excel.py + services/generador_pdf.py / views/ + static/
  (azul #14213D, dorado #B8923D).
- Orden de construcción: ver PLAN.md (1 cruce, 2 backend reglas, 3 rutas Flask,
  4 PDF/ZIP, 5 interfaz). Cada etapa se valida con cifras de control
  (19/3/1 y 3 inconsistencias) + tester-datos y revisor.
