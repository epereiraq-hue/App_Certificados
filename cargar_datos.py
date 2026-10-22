"""Script para inicializar la base de datos y cargar los datos desde los archivos Excel.

Se ejecuta en TU computadora (no en Vercel). Si el archivo .env tiene DATABASE_URL,
los datos van a Supabase; si no la tiene, van a la base local SQLite.
"""

import os
import sys
from models.datos import (
    inicializar_tablas,
    contar_estudiantes,
    contar_evaluaciones,
    obtener_conexion,
)
from services.carga_excel import cargar_datos_desde_excel


def main():
    print("=" * 60)
    print("Iniciando proceso de carga de datos...")
    print("=" * 60)

    try:
        # LADRILLO: variable tipo str que dice si se cargó en Supabase o en SQLite.
        conexion, motor = obtener_conexion()
        conexion.close()

        # LADRILLO: CONDICIONAL 1. Hay DATABASE_URL pero no conectó -> abortar.
        # Sin esto, el script "triunfaría" cargando en SQLite y Supabase quedaría vacío
        # (y la app en Vercel fallaría).
        if motor == "sqlite" and os.getenv("DATABASE_URL", "").strip():
            print(
                "\n[ERROR DE CONEXIÓN]: DATABASE_URL está definida en .env, pero no se "
                "pudo conectar a Supabase. Revisa la cadena de conexión antes de seguir.",
                file=sys.stderr,
            )
            sys.exit(1)

        # LADRILLO: CONDICIONAL 2. Sin DATABASE_URL se carga en la base local.
        if motor == "sqlite":
            print("\n[AVISO] No hay DATABASE_URL: se cargará en la base LOCAL (SQLite).")
            print("        Para Vercel debes cargar en Supabase configurando DATABASE_URL.")
        else:
            print("\n[OK] Cargando en Supabase (PostgreSQL).")

        print("\n1. Inicializando tablas en la base de datos...")
        inicializar_tablas()
        print("   Tablas 'estudiantes' y 'evaluaciones' verificadas/creadas con éxito.")

        print("\n2. Leyendo archivos Excel y cargando registros...")
        cargados_est, cargados_eva = cargar_datos_desde_excel()
        print(f"   Registros procesados del maestro: {cargados_est}")
        print(f"   Registros procesados de evaluaciones: {cargados_eva}")

        print("\n3. Verificando conteo de registros en la base de datos...")
        total_est = contar_estudiantes()
        total_eva = contar_evaluaciones()

        print("=" * 60)
        print(f"RESUMEN DE CARGA ({motor.upper()}):")
        print(f"- Filas guardadas en la tabla 'estudiantes': {total_est}")
        print(f"- Filas guardadas en la tabla 'evaluaciones': {total_eva}")
        print("=" * 60)
        print("Carga completada con éxito.")

    except ValueError as e:
        print(f"\n[ERROR DE CONFIGURACIÓN]: {e}", file=sys.stderr)
        print("Por favor, asegúrese de que el archivo .env contiene una variable DATABASE_URL válida.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\n[ERROR DE ARCHIVO]: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR EN LA CONEXIÓN O CARGA]: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
