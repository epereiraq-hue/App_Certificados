"""Módulo de Lógica de Negocio y Reglas de Certificación.

Implementa las reglas R1 a R6 especificadas en AGENTS.md.
Obtiene los datos exclusivamente a través del módulo models.datos.
"""

from typing import Any, Dict, List
from models.datos import obtener_todos_estudiantes, obtener_todas_evaluaciones

# LADRILLO: variables tipo int/float con los limites del negocio (AGENTS.md R3-R5).
# Los limites INCLUYEN el valor (>=).
NOTA_MINIMA = 70
ASISTENCIA_MINIMA = 80
ASISTENCIA_INCONSISTENCIA_LIMITE = 50


# LADRILLO: FUNCION que calcula un promedio.
# Entrada: lista de notas (tipo list con numeros tipo float).
# Salida: promedio redondeado a 2 decimales (tipo float).
def calcular_promedio(lista_notas):
    # LADRILLO: variable tipo float (suma de todas las notas).
    total = sum(lista_notas)
    # LADRILLO: variable tipo int (cantidad de modulos cursados).
    cantidad = len(lista_notas)
    # LADRILLO: variable tipo float (division suma / cantidad).
    promedio = total / cantidad
    return round(promedio, 2)


# LADRILLO: FUNCION que decide el tipo de certificado segun AGENTS.md.
# Entrada: promedio y asistencia (tipo float, ya redondeados).
# Salida: texto (tipo str) con el tipo.
def decidir_certificado(promedio, asistencia):
    # LADRILLO: CONDICIONAL 1 (R5). Sin certificado si asistencia < 80.
    if asistencia < ASISTENCIA_MINIMA:
        return "Sin Certificado"
    # LADRILLO: CONDICIONAL 2 (R3). Aprobacion si promedio >= 70 y asistencia >= 80.
    elif promedio >= NOTA_MINIMA:
        return "Aprobación"
    # LADRILLO: CONDICIONAL 3 (R4). Lo que queda es Participacion.
    else:
        return "Participación"


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

    # LADRILLO: BUCLE que recorre cada grupo de identificacion + programa (R1).
    # Todas las llaves únicas (union de maestro y evaluaciones).
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

        # Estudiante evaluado presente en maestro: calculamos con las FUNCIONES validadas.
        est = maestro_dict[key]
        evals = eval_dict[key]

        # LADRILLO: variables tipo list (notas y asistencias de los modulos).
        lista_notas = [float(e.get("nota") or 0) for e in evals]
        lista_asist = [float(e.get("asistencia_pct") or 0) for e in evals]
        # LADRILLO: variable tipo int (modulos cursados).
        n_evals = len(evals)

        # LADRILLO: llamadas a la FUNCION calcular_promedio (R2).
        promedio_nota = calcular_promedio(lista_notas)
        promedio_asist = calcular_promedio(lista_asist)

        # LADRILLO: llamada a la FUNCION decidir_certificado (R3-R5).
        # Caso especial R6: asistencia menor a 50 % es inconsistencia y no se certifica.
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
        else:
            estado_cert = decidir_certificado(promedio_nota, promedio_asist)
            # LADRILLO: CONDICIONALES para contar segun lo decidido.
            if estado_cert == "Aprobación":
                aprobacion_cnt += 1
            elif estado_cert == "Participación":
                participacion_cnt += 1
            else:
                sin_certificado_cnt += 1

        estudiantes_procesados.append({
            "identificacion": ident,
            "nombre_completo": est["nombre_completo"],
            "correo": est["correo"],
            "programa": prog,
            "cohorte": est["cohorte"],
            "modulos": n_evals,
            "promedio_nota": promedio_nota,
            "promedio_asistencia": promedio_asist,
            "estado_certificado": estado_cert,
            "es_aprobado": estado_cert == "Aprobación",
            "es_participacion": estado_cert == "Participación",
            "es_sin_certificado": estado_cert == "Sin Certificado"
        })

    # Ordenar tabla por programa y nombre para el salon.
    estudiantes_procesados.sort(key=lambda x: (x["programa"], x["nombre_completo"]))

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
