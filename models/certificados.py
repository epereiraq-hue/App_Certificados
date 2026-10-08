"""Módulo de Lógica de Negocio y Reglas de Certificación.

Implementa las reglas R1 a R6 especificadas en AGENTS.md.
Obtiene los datos exclusivamente a través del módulo models.datos.
"""

from typing import Any, Dict, List
from models.datos import obtener_todos_estudiantes, obtener_todas_evaluaciones

# Constantes de negocio
NOTA_MINIMA = 70
ASISTENCIA_MINIMA = 80
ASISTENCIA_INCONSISTENCIA_LIMITE = 50


def obtener_resumen_certificados() -> Dict[str, Any]:
    """Procesa los datos de estudiantes y evaluaciones aplicando las reglas R1-R6.

    Retorna un diccionario con:
    - conteos: {'aprobacion': int, 'participacion': int, 'sin_certificado': int}
    - estudiantes: Lista de diccionarios con el detalle de cada estudiante evaluado
    - inconsistencias: Lista de alertas de inconsistencias detectadas
    """
    lista_estudiantes = obtener_todos_estudiantes()
    lista_evaluaciones = obtener_todas_evaluaciones()

    # Mapeo de maestro por (identificacion, programa)
    maestro_dict = {}
    for est in lista_estudiantes:
        ident = str(est.get("identificacion", "")).strip()
        prog = str(est.get("programa", "")).strip()
        key = (ident, prog)
        maestro_dict[key] = {
            "identificacion": ident,
            "nombre_completo": str(est.get("nombre_completo", "")).strip(),
            "correo": str(est.get("correo", "")).strip(),
            "programa": prog,
            "cohorte": str(est.get("cohorte", "")).strip(),
        }

    # Mapeo de evaluaciones por (identificacion, programa)
    eval_dict = {}
    for ev in lista_evaluaciones:
        ident = str(ev.get("identificacion", "")).strip()
        prog = str(ev.get("programa", "")).strip()
        key = (ident, prog)
        if key not in eval_dict:
            eval_dict[key] = []
        eval_dict[key].append(ev)

    inconsistencias = []
    estudiantes_procesados = []

    aprobacion_cnt = 0
    participacion_cnt = 0
    sin_certificado_cnt = 0

    # Todas las llaves únicas
    todas_llaves = set(list(maestro_dict.keys()) + list(eval_dict.keys()))

    for key in sorted(todas_llaves, key=lambda x: (x[1], x[0])):
        ident, prog = key
        en_maestro = key in maestro_dict
        en_eval = key in eval_dict

        # Inconsistencia 1: Estudiante en maestro sin evaluaciones
        if en_maestro and not en_eval:
            est = maestro_dict[key]
            inconsistencias.append({
                "tipo": "Sin Evaluaciones",
                "identificacion": ident,
                "nombre_completo": est["nombre_completo"],
                "programa": prog,
                "detalle": f"El estudiante {est['nombre_completo']} ({ident}) está registrado en el Maestro pero no posee evaluaciones."
            })
            continue

        # Inconsistencia 2: Evaluaciones que no están en el maestro
        if en_eval and not en_maestro:
            inconsistencias.append({
                "tipo": "No Registrado en Maestro",
                "identificacion": ident,
                "nombre_completo": "No Registrado",
                "programa": prog,
                "detalle": f"Existen evaluaciones para la identificación {ident} en el programa '{prog}', pero no existe en el Maestro de Estudiantes."
            })
            continue

        # Estudiante evaluado presente en maestro
        est = maestro_dict[key]
        evals = eval_dict[key]

        total_notas = sum(float(e.get("nota") or 0) for e in evals)
        total_asist = sum(float(e.get("asistencia_pct") or 0) for e in evals)
        n_evals = len(evals)

        promedio_nota = round(total_notas / n_evals, 2)
        promedio_asist = round(total_asist / n_evals, 2)

        # Reglas R3, R4, R5, R6
        if promedio_asist < ASISTENCIA_INCONSISTENCIA_LIMITE:
            # Inconsistencia 3: Asistencia menor a 50%
            inconsistencias.append({
                "tipo": "Asistencia Crítica (<50%)",
                "identificacion": ident,
                "nombre_completo": est["nombre_completo"],
                "programa": prog,
                "detalle": f"El estudiante {est['nombre_completo']} ({ident}) presenta una asistencia del {promedio_asist}%, inferior al mínimo de 50%."
            })
            sin_certificado_cnt += 1
            estado_cert = "Sin Certificado"
        elif promedio_nota >= NOTA_MINIMA and promedio_asist >= ASISTENCIA_MINIMA:
            aprobacion_cnt += 1
            estado_cert = "Aprobación"
        elif promedio_nota < NOTA_MINIMA and promedio_asist >= ASISTENCIA_MINIMA:
            participacion_cnt += 1
            estado_cert = "Participación"
        else:
            sin_certificado_cnt += 1
            estado_cert = "Sin Certificado"

        estudiantes_procesados.append({
            "identificacion": ident,
            "nombre_completo": est["nombre_completo"],
            "correo": est["correo"],
            "programa": prog,
            "cohorte": est["cohorte"],
            "promedio_nota": promedio_nota,
            "promedio_asistencia": promedio_asist,
            "estado_certificado": estado_cert,
            "es_aprobado": estado_cert == "Aprobación",
            "es_participacion": estado_cert == "Participación",
            "es_sin_certificado": estado_cert == "Sin Certificado"
        })

    return {
        "conteos": {
            "aprobacion": aprobacion_cnt,
            "participacion": participacion_cnt,
            "sin_certificado": sin_certificado_cnt,
            "inconsistencias": len(inconsistencias)
        },
        "estudiantes": estudiantes_procesados,
        "inconsistencias": inconsistencias
    }
