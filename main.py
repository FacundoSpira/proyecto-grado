from itertools import combinations, product
from timeit import default_timer as timer

import pulp as pl

from variables_to_csv import create_schedule_csv

start = timer()

# ==== CONJUNTOS ====

D = [1, 2, 4]  # conjunto de días del calendario

C = [
    "cDiv",
    "gal1",
    "cDivv",
    "gal2",
    "pye",
    "md1",
    "md2",
    "p1",
    "p2",
    "tProg",
]  # conjunto de unidades curriculares

T = [1, 2, 3]  # conjunto de turnos

Td = {d: [1, 2] if d == 3 else T for d in D}  # conjunto de turnos para el día d

S = [
    1,
    2,
    3,
    4,
    5,
]  # conjunto de semestres. Cada semestre representa una altura de la carrera que la unidad curricular puede ser sugerida

K = ["computacion"]  # conjunto de carreras

SUG = [
    ("cDiv", 1, "computacion"),
    ("gal1", 1, "computacion"),
    ("cDivv", 2, "computacion"),
    ("gal2", 2, "computacion"),
    ("pye", 3, "computacion"),
    ("md1", 3, "computacion"),
    ("md2", 4, "computacion"),
    ("p1", 4, "computacion"),
    ("p2", 5, "computacion"),
    ("tProg", 5, "computacion"),
]  # conjunto de triplas donde la unidad curricular c se sugiere en el semestre s para la carrera k

PA = (
    []
)  # conjunto de triplas donde la unidad curricular c se asigna en el dia d en el turno t

P = [
    ("cDiv", "cDivv"),
    ("gal1", "gal2"),
    ("cDivv", "pye"),
    ("gal2", "p1"),
]  # conjunto de pares de UC donde la UC 1 es previa de la UC 2

# Pares de conjuntos frecuentes
PARES_CURSOS = list(combinations(C, 2))  # Esto genera (c1,c2) donde c1 < c2
PARES_DIAS = list(product(D, D))

# Diccionario de búsqueda para cursos en el mismo semetre
cursos_mismo_semestre = {
    (c1, c2): True
    for (c1, s1, k1) in SUG
    for (c2, s2, k2) in SUG
    if c1 != c2 and s1 == s2 and k1 == k2
}

# ==== PARÁMETROS ====

cp = {
    (d, t): 70 for d, t in [(d, t) for d in D for t in Td[d]]
}  # capacidad total del día d en el turno t

fac_cp = 1  # porcentaje que se decide usar de la capacidad

ins = {
    "cDiv": 50,
    "gal1": 50,
    "cDivv": 40,
    "gal2": 20,
    "pye": 50,
    "md1": 40,
    "md2": 20,
    "p1": 20,
    "p2": 15,
    "tProg": 15,
}  # cantidad de inscriptos en la unidad curricular c

co = {
    (c1, c2): 0 if c1 != c2 else ins[c1] for c1, c2 in PARES_CURSOS
}  # cantidad de estudiantes incriptos en simultáneo en las UC c1 y c2

# ==== FUNCIONES AUXILIARES ====


# Distancia entre los días d1 y d2 del conjunto de días en el calendario
def dist(d1, d2):
    return abs(d1 - d2)


# Distancia en semestres entre las unidades curriculares c1 y c2
def get_dist_sem(c1, c2):
    # Encuentra las carreras en las que ambos cursos están sugeridos
    careers_in_common = [
        k
        for (_, _, k) in SUG
        if any((c1, s1, k) in SUG for s1 in S) and any((c2, s2, k) in SUG for s2 in S)
    ]

    # Calcula la distancia mínima en semestres para las carreras en común
    if careers_in_common:
        distances = []
        for k in careers_in_common:
            semester_c1 = [s for c, s, kk in SUG if c == c1 and kk == k][0]
            semester_c2 = [s for c, s, kk in SUG if c == c2 and kk == k][0]

            # Calcula la distancia mínima para la carrera k específica
            distances.append(abs(semester_c1 - semester_c2))

        # Retorna la mínima distancia encontrada entre las carreras comunes
        return min(distances)
    else:
        # Devuelve |S| si no hay carreras en común entre c1 y c2
        return len(S)


# Precalcula la distancia en semestres entre todas las UC
dist_sem = {(c1, c2): get_dist_sem(c1, c2) for c1, c2 in PARES_CURSOS}

# ==== VARIABLES DE DECISIÓN ====

# Variable que vale 1 si la UC c se asigna al día d en el turno t
x = pl.LpVariable.dicts("x", (C, D, T), cat=pl.LpBinary)

# Variable que vale 1 si la UC c1 se asigna al día d1 y la UC c2 se asigna al día d2
y = pl.LpVariable.dicts(
    "y",
    ((c1, d1, c2, d2) for c1, c2 in PARES_CURSOS for d1, d2 in PARES_DIAS),
    cat="Binary",
)

# ==== FUNCION OBJETIVO ====

problem = pl.LpProblem("Optimizacion_Calendario", pl.LpMinimize)

# Valor máximo de concurrencia entre UC diferentes. Se utiliza para normalizar la concurrencia entre dos UC.
max_co = max(co[c1, c2] for c1, c2 in co if c1 != c2) + 1

problem += pl.lpSum(
    (1 / (dist(d1, d2) + 1))
    * (
        pl.lpSum(
            (co[c1, c2] / max_co + 1 / (dist_sem[c1, c2] + 1)) * y[c1, d1, c2, d2]
            for c1, c2 in PARES_CURSOS
            if c1 != c2
        )
        - pl.lpSum(
            (y[c1, d1, c2, d2] if (c1, d1, c2, d2) in y else y[c2, d2, c1, d1])
            for c1, c2 in P
        )
    )
    for d1, d2 in PARES_DIAS
)

# ==== RESTRICCIONES ====

# La evaluación de una UC se asigna a único día y turno:
for c in C:
    problem += (
        pl.lpSum(x[c][d][t] for d in D for t in Td[d]) == 1,
        f"AsignacionUnica_{c}",
    )

# Si dos UC están sugeridas en el mismo semestre para la misma carrera, se asignan a días distintos
for d in D:
    for c1, c2 in cursos_mismo_semestre:
        problem += (
            pl.lpSum(x[c1][d][t] + x[c2][d][t] for t in Td[d]) <= 1,
            f"Dias_Distintos_{c1}_{c2}_Dia_{d}",
        )

# No se puede superar la capacidad disponible de los salones, teniendo en cuenta el factor de capacidad, para cada día y turno
for d in D:
    for t in Td[d]:
        problem += (
            pl.lpSum(ins[c] * x[c][d][t] for c in C) <= cp[d, t] * fac_cp,
            f"Capacidad_{d}_{t}",
        )

# Las evaluaciones que se pre-asignan a un día y turno, se asignan en ese día y turno.
for c, d, t in PA:
    problem += x[c][d][t] == 1, f"Pre_asignacion_{c}_{d}_{t}"

# Garantiza el valor correcto de y. Es decir, asegura que y_{c_1,c_2,d_1,d_2} valga 1 si y solamente si las x correspondientes valen 1. Para esto se aplican 3 restricciones.
for c1, c2 in PARES_CURSOS:
    for d1, d2 in PARES_DIAS:
        problem += (
            y[c1, d1, c2, d2] <= pl.lpSum(x[c1][d1][t1] for t1 in Td[d1]),
            f"Restriccion_y_r1_{c1}_{d1}_{c2}_{d2}",
        )

        problem += (
            y[c1, d1, c2, d2] <= pl.lpSum(x[c2][d2][t2] for t2 in Td[d2]),
            f"Restriccion_y_r2_{c1}_{d1}_{c2}_{d2}",
        )

        problem += (
            y[c1, d1, c2, d2]
            >= pl.lpSum(x[c1][d1][t1] for t1 in Td[d1])
            + pl.lpSum(x[c2][d2][t2] for t2 in Td[d2])
            - 1,
            f"Restriccion_y_r3_{c1}_{d1}_{c2}_{d2}",
        )

# ==== SOLUCIÓN ====
solver = pl.PULP_CBC_CMD(
    threads=12,
    msg=1,  # Mostrar output para debug
    timeLimit=3600,  # Límite de tiempo de 1 hora
    gapRel=0.05,  # Gap de optimalidad del 5%
)

status = problem.solve(solver)
print("Status:", pl.LpStatus[problem.status])

for v in problem.variables():
    print(v.name, "=", v.varValue)

print("Valor óptimo de la función objetivo: ", pl.value(problem.objective))

end = timer()
execution_time = end - start

print(f"Tiempo de ejecución: {execution_time:.2f} segundos")
print(f"                     {execution_time/60:.2f} minutos")
print(f"                     {execution_time/3600:.2f} horas")

create_schedule_csv(problem.variables(), Td, "schedule.csv")
