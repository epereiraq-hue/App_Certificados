# App_Certificados

Greenfield project. No code, no manifest, no README, no tests yet. Only input data exists in `Insumos/`. Any app/scripts built here generate certificates from those two workbooks.

## Inputs (read-only, never overwrite)

- `Insumos/Maestro_Estudiantes.xlsx` — sheet `Estudiantes`, 24 rows + header:
  `Identificacion | Nombre_Completo | Correo | Programa | Cohorte`
- `Insumos/Registro_Evaluaciones.xlsx` — sheet `Evaluaciones`, 88 rows + header:
  `Identificacion | Programa | Modulo | Nota | Asistencia_Pct | Fecha_Cierre`

Programs: `Técnico en IA Aplicada` (16 students, 4 módulos) and `Excel Avanzado para Negocios` (8 students, 3 módulos). All `Cohorte = 2026-A`. `Fecha_Cierre` is ISO `YYYY-MM-DD` per módulo.

## Data gotchas (verified, handle them)

- Join key is `(Identificacion, Programa)`. Treat `Identificacion` as **text**, not number (9-digit IDs).
- Deliberate edge cases in the fixtures:
  - `304560321` (Espinoza León, IA) is in Maestro but has **zero** evaluation rows.
  - `999880777` has 4 IA evaluation rows but is **missing from Maestro** (orphan).
  - `111230984` is a dropout: `Nota = 0` with `Asistencia_Pct = 20 / 0` in Módulo 3–4.
  - `116890234`, `205430876` have failing-range notas (~50–65).
- No pass/fail thresholds, approval rules, or certificate templates are defined anywhere in the repo. Do not invent them — ask the user.
- Accent mojibake: raw XML shows `TǸcnico` / `M��dulo` for `Técnico` / `Módulo`. Read workbooks with a real xlsx parser (UTF-8) and normalize to NFC; never byte-match program/module names.

## Environment quirks

- Path contains spaces, `-`, and accents (`OneDrive - Era Ecotank.../CI- Control Interno/...`). Quote paths in PowerShell; this is a OneDrive/SharePoint-synced folder (workbook metadata points at `lacasadeltanque-my.sharepoint.com`), so avoid lock conflicts with Excel open and keep generated outputs out of `Insumos/`.
- Windows PowerShell 5.1 with **no Python, Node, or git repo** at last check (`python3`, `py`, `node` all missing). Verify toolchain before building; if adding one, document the exact install/run commands here.
