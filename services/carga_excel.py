"""Servicio para lectura, validación y carga de archivos Excel en la base de datos."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd

from models.datos import reemplazar_estudiantes, reemplazar_evaluaciones

# Columnas esperadas en cada archivo/hoja
COLUMNAS_ESPERADAS_ESTUDIANTES = [
    "identificacion",
    "nombre_completo",
    "correo",
    "programa",
    "cohorte",
]

COLUMNAS_ESPERADAS_EVALUACIONES = [
    "identificacion",
    "programa",
    "modulo",
    "nota",
    "asistencia_pct",
    "fecha_cierre",
]


def normalizar_nombre_columna(col: str) -> str:
    """Normaliza el nombre de una columna a minúsculas y sin espacios adicionales."""
    return str(col).strip().lower()


def procesar_maestro_estudiantes(
    origen: Union[str, Path, Any]
) -> List[Dict[str, Any]]:
    """Lee y valida la hoja 'Estudiantes' del archivo maestro de estudiantes.

    Args:
        origen: Ruta al archivo Excel o buffer en memoria (UploadedFile).

    Returns:
        Lista de diccionarios con las filas procesadas.
    """
    df = pd.read_excel(
        origen,
        sheet_name="Estudiantes",
        dtype={"Identificacion": str},
    )

    # Mapeo de columnas normalizadas
    columnas_map = {col: normalizar_nombre_columna(col) for col in df.columns}
    df = df.rename(columns=columnas_map)

    # Validar presencia de columnas obligatorias
    faltantes = [col for col in COLUMNAS_ESPERADAS_ESTUDIANTES if col not in df.columns]
    if faltantes:
        raise ValueError(
            f"El archivo de Estudiantes no contiene las columnas requeridas: {faltantes}"
        )

    # Filtrar filas vacías o donde la identificación esté en blanco
    df = df.dropna(subset=["identificacion"])
    df["identificacion"] = (
        df["identificacion"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    )
    df = df[df["identificacion"] != ""]

    registros: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        registros.append(
            {
                "identificacion": str(row["identificacion"]).strip(),
                "nombre_completo": str(row.get("nombre_completo", "")).strip() if pd.notna(row.get("nombre_completo")) else "",
                "correo": str(row.get("correo", "")).strip() if pd.notna(row.get("correo")) else "",
                "programa": str(row.get("programa", "")).strip() if pd.notna(row.get("programa")) else "",
                "cohorte": str(row.get("cohorte", "")).strip() if pd.notna(row.get("cohorte")) else "",
            }
        )

    return registros


def procesar_registro_evaluaciones(
    origen: Union[str, Path, Any]
) -> List[Dict[str, Any]]:
    """Lee y valida la hoja 'Evaluaciones' del archivo de evaluaciones.

    Args:
        origen: Ruta al archivo Excel o buffer en memoria (UploadedFile).

    Returns:
        Lista de diccionarios con las filas procesadas.
    """
    df = pd.read_excel(
        origen,
        sheet_name="Evaluaciones",
        dtype={"Identificacion": str},
    )

    columnas_map = {col: normalizar_nombre_columna(col) for col in df.columns}
    df = df.rename(columns=columnas_map)

    faltantes = [col for col in COLUMNAS_ESPERADAS_EVALUACIONES if col not in df.columns]
    if faltantes:
        raise ValueError(
            f"El archivo de Evaluaciones no contiene las columnas requeridas: {faltantes}"
        )

    df = df.dropna(subset=["identificacion"])
    df["identificacion"] = (
        df["identificacion"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    )
    df = df[df["identificacion"] != ""]

    registros: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        # Formatear fecha si es datetime o Timestamp
        fecha_val = row.get("fecha_cierre")
        if pd.isna(fecha_val):
            fecha_str = ""
        elif hasattr(fecha_val, "strftime"):
            fecha_str = fecha_val.strftime("%Y-%m-%d")
        else:
            fecha_str = str(fecha_val).strip()

        nota_val = row.get("nota")
        asist_val = row.get("asistencia_pct")

        registros.append(
            {
                "identificacion": str(row["identificacion"]).strip(),
                "programa": str(row.get("programa", "")).strip() if pd.notna(row.get("programa")) else "",
                "modulo": str(row.get("modulo", "")).strip() if pd.notna(row.get("modulo")) else "",
                "nota": float(nota_val) if pd.notna(nota_val) else None,
                "asistencia_pct": float(asist_val) if pd.notna(asist_val) else None,
                "fecha_cierre": fecha_str,
            }
        )

    return registros


def cargar_datos_desde_excel(
    ruta_maestro: Optional[Union[str, Path]] = None,
    ruta_evaluaciones: Optional[Union[str, Path]] = None,
) -> Tuple[int, int]:
    """Carga los datos de los Excel en la base de datos Supabase.

    Si no se especifican rutas, busca por defecto en la carpeta 'insumos/'.
    Retorna una tupla (cantidad_estudiantes, cantidad_evaluaciones).
    """
    base_dir = Path(__file__).resolve().parent.parent

    if ruta_maestro is None:
        ruta_maestro = base_dir / "insumos" / "Maestro_Estudiantes.xlsx"
    else:
        ruta_maestro = Path(ruta_maestro)

    if ruta_evaluaciones is None:
        ruta_evaluaciones = base_dir / "insumos" / "Registro_Evaluaciones.xlsx"
    else:
        ruta_evaluaciones = Path(ruta_evaluaciones)

    if not ruta_maestro.exists():
        raise FileNotFoundError(f"No se encontró el archivo maestro en: {ruta_maestro}")

    if not ruta_evaluaciones.exists():
        raise FileNotFoundError(f"No se encontró el archivo de evaluaciones en: {ruta_evaluaciones}")

    estudiantes = procesar_maestro_estudiantes(ruta_maestro)
    evaluaciones = procesar_registro_evaluaciones(ruta_evaluaciones)

    total_estudiantes = reemplazar_estudiantes(estudiantes)
    total_evaluaciones = reemplazar_evaluaciones(evaluaciones)

    return total_estudiantes, total_evaluaciones
