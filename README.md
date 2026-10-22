# App_Certificados

Aplicación web (Flask) de la Academia Horizonte para generar certificados por
cohorte: lee dos Excel, guarda los datos en PostgreSQL (Supabase), aplica las
reglas del negocio y muestra el tablero con las inconsistencias.

- Reglas del negocio y arquitectura: ver `AGENTS.md`.
- Orden de construcción: ver `PLAN.md`.

## 1. Correr en local (Windows)

Requisitos: [uv](https://docs.astral.sh/uv/) (no se usa `pip`).

```powershell
uv sync                 # instala las dependencias
uv run python cargar_datos.py   # crea las tablas y carga los Excel de Insumos/
uv run python app.py            # abre http://localhost:5000
```

También puedes hacer doble clic en `iniciar_app.bat`.

Sin `DATABASE_URL` en el archivo `.env`, la app usa una base SQLite local
(`app_certificados.db`) solo para trabajar en tu computadora.

### Variables de entorno (`.env`, no se sube a GitHub)

```
DATABASE_URL=postgresql://usuario:clave@host:puerto/base
```

La plantilla vacía está en `.env.ejemplo`.

## 2. Desplegar en Vercel

Vercel detecta Flask automáticamente: busca un objeto llamado `app` dentro de
`app.py`, que es justo lo que tiene este proyecto. No hace falta `vercel.json`.

### 2.1 Preparar Supabase (una sola vez, desde tu computadora)

Vercel no tiene disco: el archivo `app_certificados.db` no sobrevive ahí. Por eso
la nube usa **Supabase** obligatoriamente.

1. Crea el proyecto en Supabase y copia la cadena de conexión (Connection string → URI).
2. Ponla en tu `.env` local como `DATABASE_URL`.
3. Carga los datos (crea las tablas y sube los 2 Excel):

```powershell
uv run python cargar_datos.py
```

Deben salir 24 estudiantes y 88 evaluaciones.

### 2.2 Subir el código a GitHub

```powershell
git add .
git commit -m "Preparar despliegue en Vercel con Supabase"
git push origin main
```

### 2.3 Crear el proyecto en Vercel

1. En Vercel: **Add New → Project** e importa `epereiraq-hue/App_Certificados`.
2. Framework Preset: **Flask** (lo detecta solo). No cambies build ni output.
3. En **Environment Variables** agrega:
   - `DATABASE_URL` = la cadena de Supabase. En Supabase usa
     **Connect → Connection string → URI** y elige el **pooler**
     (el host termina en `pooler.supabase.com`). Copia la cadena completa,
     incluido el `?sslmode=require` del final (eso es el cifrado TLS, no el pooler).
4. **Deploy**.

### 2.4 Comprobar

- Abre la URL y mira las tarjetas: **19 Aprobación, 3 Participación, 1 Sin
  certificado y 3 inconsistencias**.
- Control: Camila `101230456` = 91.25 / 96.25 Aprobación.
- Si ves un error 500, revisa en Vercel → Deployments → Functions → Logs que
  `DATABASE_URL` esté bien escrita.

> **Ojo con `/cargar`:** esa página reemplaza TODA la base de datos y en Vercel
> queda abierta a cualquiera que tenga el enlace. No la compartas y, si el sitio
> va a ser público, conviene protegerla con una clave antes de difundirlo.

## 3. Estructura

| Carpeta | Para qué sirve |
|---|---|
| `app.py` | Crea la app Flask (punto de entrada que usa Vercel) |
| `controllers/` | Rutas; no calculan nada |
| `models/datos.py` | Único archivo que habla con la base de datos |
| `models/certificados.py` | Reglas del negocio (70 / 80) |
| `services/` | Leer Excel y generar PDF |
| `views/` | Plantillas HTML (Jinja) |
| `public/static/` | CSS e imágenes: Vercel los sirve desde `/static/...` |
| `Insumos/` | Excel de entrada (solo lectura) |
