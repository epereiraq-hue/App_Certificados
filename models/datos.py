"""Módulo de acceso y persistencia de datos (Supabase PostgreSQL con fallback SQLite local).

Este archivo es el único del sistema autorizado para comunicarse con la base de datos.
Soporta Supabase mediante psycopg (prepare_threshold=None) cuando DATABASE_URL está configurada en .env,
y conmuta a SQLite local (app_certificados.db) si DATABASE_URL no está configurada o no hay conexión.
"""

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# LADRILLO: variables de rutas. BASE_DIR es la carpeta del proyecto (donde esta app.py),
# asi la base local siempre se encuentra, sin importar desde donde se ejecute.
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "app_certificados.db"

# LADRILLO: variable tipo bool. Vercel pone VERCEL=1 automaticamente.
# En la nube NO existe el respaldo SQLite porque Vercel no guarda archivos.
EN_VERCEL = bool(os.getenv("VERCEL"))


def _es_postgres() -> bool:
    url = os.getenv("DATABASE_URL")
    return bool(url and url.strip())


def obtener_conexion() -> Tuple[Any, str]:
    """Retorna una tupla (conexion, tipo_db) donde tipo_db es 'postgres' o 'sqlite'."""
    url = os.getenv("DATABASE_URL")
    # LADRILLO: CONDICIONAL 1. Hay DATABASE_URL -> intentamos Supabase/PostgreSQL.
    if url and url.strip():
        try:
            import psycopg
            conn = psycopg.connect(url.strip(), prepare_threshold=None)
            return conn, "postgres"
        except Exception as e:
            # En la nube NO se cae a SQLite: es mejor un error claro que un tablero vacio.
            if EN_VERCEL:
                raise RuntimeError(
                    "No se pudo conectar a Supabase. Revisa la variable DATABASE_URL "
                    f"en Vercel. Detalle: {e}"
                ) from e
            print(f"[WARN] No se pudo conectar a Supabase/PostgreSQL ({e}). Usando SQLite local.")

    # LADRILLO: CONDICIONAL 2. Sin DATABASE_URL en Vercel -> error explicito.
    if EN_VERCEL:
        raise RuntimeError(
            "Falta la variable DATABASE_URL en Vercel. "
            "En la nube la app solo funciona con Supabase (Vercel no guarda archivos)."
        )

    # LADRILLO: respaldo SOLO para trabajar en tu computadora.
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"


def inicializar_tablas() -> None:
    """Crea las tablas 'estudiantes' y 'evaluaciones' si aún no existen."""
    conn, db_type = obtener_conexion()
    try:
        cur = conn.cursor()
        if db_type == "postgres":
            cur.execute("""
            CREATE TABLE IF NOT EXISTS estudiantes (
                identificacion TEXT PRIMARY KEY,
                nombre_completo TEXT,
                correo TEXT,
                programa TEXT,
                cohorte TEXT
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS evaluaciones (
                id SERIAL PRIMARY KEY,
                identificacion TEXT,
                programa TEXT,
                modulo TEXT,
                nota NUMERIC,
                asistencia_pct NUMERIC,
                fecha_cierre TEXT
            );
            """)
        else:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS estudiantes (
                identificacion TEXT PRIMARY KEY,
                nombre_completo TEXT,
                correo TEXT,
                programa TEXT,
                cohorte TEXT
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS evaluaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identificacion TEXT,
                programa TEXT,
                modulo TEXT,
                nota REAL,
                asistencia_pct REAL,
                fecha_cierre TEXT
            );
            """)
        conn.commit()
    finally:
        conn.close()


def reemplazar_estudiantes(registros: List[Dict[str, Any]]) -> int:
    """Limpia la tabla 'estudiantes' e inserta los registros proporcionados.

    Retorna la cantidad de registros insertados.
    """
    datos = [
        (
            str(r.get("identificacion", "")).strip(),
            str(r.get("nombre_completo", "")).strip() if r.get("nombre_completo") is not None else "",
            str(r.get("correo", "")).strip() if r.get("correo") is not None else "",
            str(r.get("programa", "")).strip() if r.get("programa") is not None else "",
            str(r.get("cohorte", "")).strip() if r.get("cohorte") is not None else "",
        )
        for r in registros
    ]

    conn, db_type = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM estudiantes;")
        placeholder = "%s" if db_type == "postgres" else "?"
        query = f"INSERT INTO estudiantes (identificacion, nombre_completo, correo, programa, cohorte) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
        if datos:
            cur.executemany(query, datos)
        conn.commit()
        return len(datos)
    finally:
        conn.close()


def reemplazar_evaluaciones(registros: List[Dict[str, Any]]) -> int:
    """Limpia la tabla 'evaluaciones' e inserta los registros proporcionados.

    Retorna la cantidad de registros insertados.
    """
    datos = [
        (
            str(r.get("identificacion", "")).strip(),
            str(r.get("programa", "")).strip() if r.get("programa") is not None else "",
            str(r.get("modulo", "")).strip() if r.get("modulo") is not None else "",
            r.get("nota"),
            r.get("asistencia_pct"),
            str(r.get("fecha_cierre", "")).strip() if r.get("fecha_cierre") is not None else "",
        )
        for r in registros
    ]

    conn, db_type = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM evaluaciones;")
        placeholder = "%s" if db_type == "postgres" else "?"
        query = f"INSERT INTO evaluaciones (identificacion, programa, modulo, nota, asistencia_pct, fecha_cierre) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
        if datos:
            cur.executemany(query, datos)
        conn.commit()
        return len(datos)
    finally:
        conn.close()


def contar_estudiantes() -> int:
    """Retorna el número total de registros en la tabla 'estudiantes'."""
    conn, _ = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM estudiantes;")
        res = cur.fetchone()
        return int(res[0]) if res else 0
    finally:
        conn.close()


def contar_evaluaciones() -> int:
    """Retorna el número total de registros en la tabla 'evaluaciones'."""
    conn, _ = obtener_conexion()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM evaluaciones;")
        res = cur.fetchone()
        return int(res[0]) if res else 0
    finally:
        conn.close()


def obtener_todos_estudiantes() -> List[Dict[str, Any]]:
    """Obtiene todos los registros de la tabla 'estudiantes' como diccionarios."""
    conn, db_type = obtener_conexion()
    try:
        if db_type == "postgres":
            from psycopg.rows import dict_row
            cur = conn.cursor(row_factory=dict_row)
            cur.execute("SELECT identificacion, nombre_completo, correo, programa, cohorte FROM estudiantes;")
            return list(cur.fetchall())
        else:
            cur = conn.cursor()
            cur.execute("SELECT identificacion, nombre_completo, correo, programa, cohorte FROM estudiantes;")
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def obtener_todas_evaluaciones() -> List[Dict[str, Any]]:
    """Obtiene todos los registros de la tabla 'evaluaciones' como diccionarios."""
    conn, db_type = obtener_conexion()
    try:
        if db_type == "postgres":
            from psycopg.rows import dict_row
            cur = conn.cursor(row_factory=dict_row)
            cur.execute("SELECT id, identificacion, programa, modulo, nota, asistencia_pct, fecha_cierre FROM evaluaciones;")
            return list(cur.fetchall())
        else:
            cur = conn.cursor()
            cur.execute("SELECT id, identificacion, programa, modulo, nota, asistencia_pct, fecha_cierre FROM evaluaciones;")
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()
