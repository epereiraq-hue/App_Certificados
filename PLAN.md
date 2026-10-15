# PLAN de implementación — App Certificados Academia Horizonte

> Modo Plan. No hay código todavía. Este archivo manda el orden de construcción.

## Idea en una frase
Primero probamos que los números salen bien, luego hacemos la cocina (Flask),
al final el salón (HTML bonito).

## Orden de las etapas

### Etapa 1 — Validar el cruce de datos (Bodega)
**Qué haré:**
- Leer los 2 Excel de `Insumos/` sin modificarlos.
- Limpiar `Identificacion` como texto sin espacios.
- Agrupar por `Identificacion + Programa`.
- Calcular Promedio y Asistencia, redondeo a 2 decimales.
- Aplicar R3/R4/R5 y detectar R6 (las 3 inconsistencias).

**Archivos que tocaremos después (todavía no):**
- `services/carga_excel.py` (leer Excel)
- `models/certificados.py` (reglas)

**Cómo validamos antes de seguir:**
- Tienen que salir las cifras de control de `AGENTS.md`:
  19 Aprobación, 3 Participación, 1 Sin certificado, 3 inconsistencias.
- Controles: Camila `101230456` = 91.25 / 96.25 Aprobación.
  Luis `402340178` = 72.0 / 81.67 Aprobación.
- Inconsistencias: `304560321` sin evaluaciones,
  `999880777` no está en maestro, Fernanda `111230984` con 36.25.
- El subagente tester-datos lo comprueba y el revisor lo revisa.
- Sin este visto bueno, no pasamos a la Etapa 2.

### Etapa 2 — Backend base + reglas (Cocina, parte 1)
**Qué haré:**
- `models/certificados.py` con `NOTA_MINIMA = 70` y `ASISTENCIA_MINIMA = 80`.
- `models/datos.py` único que habla con Supabase (`DATABASE_URL` de `.env`, `psycopg` con `prepare_threshold=None`).
- Código simple y comentado en español (variables, tipos, condicionales, bucles, funciones).

**Cómo validamos:**
- Prueba con los 2 casos control + 1 de cada tipo (Aprobación, Participación, Sin).
- Revisar que los límites 70 y 80 incluyen el valor.
- Tester + revisor.

### Etapa 3 — Backend Flask: rutas (Cocina, parte 2)
**Qué haré:**
- `app.py` crea `app` Flask, puerto 5000.
- `controllers/` con rutas: `/` tablero, `/cargar` subir 2 Excel,
  `/certificado/<identificacion>/<programa>` PDF, `/descargar-todos` ZIP.
- Los controladores no calculan, solo llaman a modelos y servicios.

**Cómo validamos:**
- Abrir `/` sin error, subir los 2 Excel de prueba y ver conteos.
- Tester prueba rutas, revisor mira que no haya lógica en controladores.

### Etapa 4 — PDF y ZIP (Cocina, parte 3)
**Qué haré:**
- `services/generador_pdf.py` con `fpdf2`, A4 horizontal, azul marino `#14213D` y dorado `#B8923D`.
- Un PDF por estudiante+programa, solo para Aprobación y Participación.
- ZIP con los 22 certificados (19+3).

**Cómo validamos:**
- Abrir 2 PDF y ver nombre, programa, promedio, asistencia y tipo.
- Contar 22 archivos en el ZIP.
- Tester + revisor.

### Etapa 5 — Interfaz HTML (Salón)
**Qué haré:**
- `views/` con Jinja, solo muestran: tablero con tabla, alertas de inconsistencias, botones de descarga.
- `static/` con estilo azul marino y dorado.
- Nada de cálculos en HTML.

**Cómo validamos:**
- Ver el tablero: 19 / 3 / 1 y las 3 alertas.
- Probar con ojos de principiante: ¿se entiende?
- Tester + revisor final con cifras de control.

## Reglas que no se rompen nunca
- No tocar `Insumos/`.
- No leer ni mostrar `.env`, no poner contraseñas en el código.
- `uv` (nunca `pip`), Python 3.12.
- Entregas pequeñas, decir qué archivo cambió y en qué capa está.
