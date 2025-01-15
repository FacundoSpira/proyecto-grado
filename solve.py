from timeit import default_timer as timer
from typing import TypedDict

import os
import pulp as pl

from csv_data_to_model_data import load_calendar_data


# Definición de un Enum para los diferentes solvers soportados
class Solver:
    CPLEX_CMD = "CPLEX_CMD"
    GUROBI_CMD = "GUROBI_CMD"
    PULP_CBC_CMD = "PULP_CBC_CMD"


class Config(TypedDict):
    solver: Solver
    gapRel: float
    maxNodes: int


def solve_model(dir_name: str, config: Config) -> tuple[float, float, dict]:
    # region CARGA DE DATOS
    datos = load_calendar_data(dir_name)

    D = datos.get("D")
    C = datos.get("C")
    Td = datos.get("Td")
    PA = datos.get("PA")
    COP = datos.get("COP")
    P = datos.get("P")
    PARES_CURSOS = datos.get("PARES_CURSOS")
    CURSOS_MISMO_SEMESTRE = datos.get("CURSOS_MISMO_SEMESTRE")
    cp = datos.get("cp")
    fac_cp = datos.get("fac_cp")
    ins = datos.get("ins")
    co = datos.get("co")
    dist_sem = datos.get("dist_sem")
    DS = datos.get("DS")
    M = datos.get("M")
    dist_peso = datos.get("dist_peso")
    # endregion

    # region DEFINICIÓN DEL PROBLEMA
    problem = pl.LpProblem("Optimizacion_Calendario", pl.LpMinimize)
    # endregion

    # region DEFINICIÓN DE VARIABLES

    # Variable que vale 1 si la UC c se asigna al día d en el turno t
    x = {}
    for c in C:
        for d in D:
            for t in Td[d]:
                x[(c, d, t)] = pl.LpVariable(f"x_{c}_{d}_{t}", cat=pl.LpBinary)

    # Variable binaria para identificar si distancia entre las evaluaciones de dos UC es ds
    w = {}
    for c1, c2 in PARES_CURSOS:
        for ds in DS:
            w[(c1, c2, ds)] = pl.LpVariable(f"w_{c1}_{c2}_{ds}", cat=pl.LpBinary)

    # Variables para definir la distancia entre las evaluaciones de dos UC
    z = {}  # Valor absoluto de la diferencia entre las evaluaciones de c1 y c2
    z_plus = {}  # Indica la parte positiva de z
    z_minus = {}  # Indica la parte negativa de z
    y = {}  # Indica si z_plus o z_minus es activo

    for c1, c2 in PARES_CURSOS:
        z[(c1, c2)] = pl.LpVariable(f"z_{c1}_{c2}", lowBound=0)
        z_plus[(c1, c2)] = pl.LpVariable(f"z_plus_{c1}_{c2}", lowBound=0)
        z_minus[(c1, c2)] = pl.LpVariable(f"z_minus_{c1}_{c2}", lowBound=0)
        y[(c1, c2)] = pl.LpVariable(f"y_{c1}_{c2}", cat=pl.LpBinary)
    # endregion

    # region DEFINICIÓN DE LA FUNCIÓN OBJETIVO

    # Valor máximo de concurrencia entre UC diferentes. Se utiliza para normalizar la concurrencia entre dos UC.
    max_co = max(co[c1, c2] for c1, c2 in co if c1 != c2) + 1

    problem += pl.lpSum(
        # Para cada par de cursos
        pl.lpSum(
            # Multiplicamos el peso de la distancia por la variable binaria correspondiente
            dist_peso[ds]
            * (co[c1, c2] / max_co + 1 / (dist_sem[c1, c2] + 1))
            * w[c1, c2, ds]
            for ds in DS
        )
        for c1, c2 in PARES_CURSOS
    ) - pl.lpSum(
        # Para los pares de previas
        pl.lpSum(
            dist_peso[ds] * (w[c1, c2, ds] if (c1, c2, ds) in w else w[c2, c1, ds])
            for ds in DS
        )
        for c1, c2 in P
    )
    # endregion

    # region DEFINICIÓN DE LAS RESTRICCIONES

    # Los cursos que tengan profesores coincidentes no pueden ser asignados el mismo dia
    for d in D:
        for c1, c2 in COP:
            problem += (
                pl.lpSum(x[c1, d, t] + x[c2, d, t] for t in Td[d]) <= 1,
                f"No_Solapamiento_COP_{c1}_{c2}_Dia_{d}",
            )

    # La evaluación de una UC se asigna a único día y turno:
    for c in C:
        problem += (
            pl.lpSum(x[c, d, t] for d in D for t in Td[d]) == 1,
            f"AsignacionUnica_{c}",
        )

    # Si dos UC están sugeridas en el mismo semestre para la misma carrera, se asignan a días distintos
    for d in D:
        for c1, c2 in CURSOS_MISMO_SEMESTRE:
            problem += (
                pl.lpSum(x[c1, d, t] + x[c2, d, t] for t in Td[d]) <= 1,
                f"Dias_Distintos_{c1}_{c2}_Dia_{d}",
            )

    # No se puede superar la capacidad disponible de los salones, teniendo en cuenta el factor de capacidad, para cada día y turno
    for d in D:
        for t in Td[d]:
            problem += (
                pl.lpSum(ins[c] * x[c, d, t] for c in C) <= cp[d, t] * fac_cp,
                f"Capacidad_{d}_{t}",
            )

    # Las evaluaciones que se pre-asignan a un día y turno, se asignan en ese día y turno.
    for c in PA.keys():
        problem += (pl.lpSum(x[c, d, t] for d, t in PA[c]) == 1, f"PreAsignacion_{c}")

    for c1, c2 in PARES_CURSOS:
        # Calcular la diferencia entre los días asignados a c1 y c2
        day_c1 = pl.lpSum(d * pl.lpSum(x[c1, d, t] for t in Td[d]) for d in D)
        day_c2 = pl.lpSum(d * pl.lpSum(x[c2, d, t] for t in Td[d]) for d in D)

        # Restricciones para hacer que z valga efectivamente la diferencia absoluta
        problem += (
            day_c1 - day_c2 == z_plus[c1, c2] - z_minus[c1, c2],
            f"Diferencia_Dias_{c1}_{c2}",
        )

        problem += (
            z[c1, c2] == z_plus[c1, c2] + z_minus[c1, c2],
            f"Distancia_Absoluta_{c1}_{c2}",
        )

        problem += pl.lpSum(w[c1, c2, ds] for ds in DS) == 1
        problem += z[c1, c2] == pl.lpSum(ds * w[c1, c2, ds] for ds in DS)

        # Usar y para controlar qué parte de z_plus o z_minus está activa
        problem += (z_plus[c1, c2] <= M * y[c1, c2], f"Control_z_plus_{c1}_{c2}")
        problem += (
            z_minus[c1, c2] <= M * (1 - y[c1, c2]),
            f"Control_z_minus_{c1}_{c2}",
        )
    # endregion

    # region SOLUCIÓN DEL PROBLEMA
    solver = None
    timeLimit = 900  # 15 minutos
    match config["solver"]:
        case Solver.GUROBI_CMD:
            solver = pl.GUROBI_CMD(
                msg=1,
                threads=12,
                timeLimit=timeLimit,
                gapRel=config["gapRel"],
                options=[
                    ("NodeLimit", config["maxNodes"]),
                ],
            )
        case Solver.CPLEX_CMD:
            solver = pl.CPLEX_CMD(
                msg=1,
                threads=12,
                timeLimit=timeLimit,
                gapRel=config["gapRel"],
                maxNodes=config["maxNodes"],
            )
        case Solver.PULP_CBC_CMD:
            solver = pl.PULP_CBC_CMD(
                msg=1,
                threads=12,
                timeLimit=timeLimit,
                gapRel=config["gapRel"],
                maxNodes=config["maxNodes"],
            )
        case _:
            raise ValueError(f"Solver {config['solver']} no soportado")

    start_time = timer()
    problem.solve(solver)
    end_time = timer()

    execution_time = end_time - start_time

    if os.environ.get("DEBUG", "false") == "true":
        print("Status:", pl.LpStatus[problem.status])

        for v in problem.variables():
            print(v.name, "=", v.varValue)

        print("Valor óptimo de la función objetivo: ", pl.value(problem.objective))

        print(f"Tiempo de ejecución: {execution_time:.2f} segundos")
        print(f"                     {execution_time/60:.2f} minutos")
        print(f"                     {execution_time/3600:.2f} horas")

    return pl.value(problem.objective), execution_time, problem.variables()
    # endregion
