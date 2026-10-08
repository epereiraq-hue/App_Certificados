"""Script para inicializar la base de datos y cargar los datos desde los archivos Excel."""

import sys
from models.datos import inicializar_tablas, contar_estudiantes, contar_evaluaciones
from services.carga_excel import cargar_datos_desde_excel


def main():
    print("=" * 60)
    print("Iniciando proceso de carga de datos hacia Supabase...")
    print("=" * 60)

    try:
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
        print("RESUMEN DE CARGA EN SUPABASE:")
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
