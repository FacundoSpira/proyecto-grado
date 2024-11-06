from itertools import combinations
from timeit import default_timer as timer

import pulp as pl

from variables_to_csv import create_schedule_csv
from csv_data_to_model_data import cargar_datos_calendario

start = timer()

# ==== FUNCIONES AUXILIARES ====



datos = cargar_datos_calendario("caso2")

D = datos.get("D")
C = datos.get("C")
T = datos.get("T")
Td = datos.get("Td")
S = datos.get("S")
K = datos.get("K")
SUG = datos.get("SUG")
PA = datos.get("PA")
P = datos.get("P")
PARES_DIAS = datos.get("PARES_DIAS")
PARES_CURSOS = datos.get("PARES_CURSOS")
cursos_mismo_semestre = datos.get("cursos_mismo_semestre")
cp = datos.get("cp")
fac_cp = datos.get("fac_cp")
ins = datos.get("ins")
co = datos.get("co")
dist_sem = datos.get("dist_sem")

def get_possible_distances(D):
            """
            Calcula todas las posibles distancias entre los días en D
            """
            distances = set()
            for d1 in D:
                for d2 in D:
                    distances.add(abs(d1 - d2))
            return sorted(list(distances))

distancias = get_possible_distances(D)

dist_peso = {dist: 1/(dist + 1) for dist in distancias}


# ==== VARIABLES DE DECISIÓN ====

# Variable que vale 1 si la UC c se asigna al día d en el turno t
x = pl.LpVariable.dicts("x", (C, D, T), cat=pl.LpBinary)

z = pl.LpVariable.dicts("z", PARES_CURSOS, lowBound=0, cat=pl.LpInteger)
z_plus = pl.LpVariable.dicts("z_plus", PARES_CURSOS, lowBound=0, cat=pl.LpInteger)
z_minus = pl.LpVariable.dicts("z_minus", PARES_CURSOS, lowBound=0, cat=pl.LpInteger)

# Variables binarias para identificar cada distancia posible

w = pl.LpVariable.dicts("w",
                        ((c1, c2, dist) for (c1, c2) in PARES_CURSOS
                        for dist in distancias),
                        cat=pl.LpBinary)

# ==== FUNCION OBJETIVO ====

problem = pl.LpProblem("Optimizacion_Calendario", pl.LpMinimize)

# Valor máximo de concurrencia entre UC diferentes. Se utiliza para normalizar la concurrencia entre dos UC.
max_co = max(co[c1, c2] for c1, c2 in co if c1 != c2) + 1

problem += pl.lpSum(
    # Para cada par de cursos
    pl.lpSum(
        # Multiplicamos el peso de la distancia por la variable binaria correspondiente
        dist_peso[dist] * w[c1, c2, dist] * (co[c1, c2] / max_co + 1 / (dist_sem[c1, c2] + 1))
        for dist in distancias
    )
    for c1, c2 in PARES_CURSOS
) - pl.lpSum(
    # Para los pares de previas
    pl.lpSum(
        dist_peso[dist] * (w[c1, c2, dist] if (c1, c2, dist) in w else w[c2, c1, dist])
        for dist in distancias
    )
    for c1, c2 in P
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
for c in PA.keys():
    problem += (pl.lpSum(x[c][d][t] for d, t in PA[c]) == 1, f"PreAsignacion_{c}")

for c1, c2 in PARES_CURSOS:
        # Calcula la diferencia entre los días asignados
        problem += (
            pl.lpSum(d * pl.lpSum(x[c1][d][t] for t in Td[d]) for d in D) -
            pl.lpSum(d * pl.lpSum(x[c2][d][t] for t in Td[d]) for d in D) ==
            z_plus[c1, c2] - z_minus[c1, c2]
        )

        # La distancia absoluta
        problem += z[c1, c2] == z_plus[c1, c2] + z_minus[c1, c2]

        # Solo una distancia puede ser seleccionada
        problem += pl.lpSum(w[c1, c2, dist] for dist in distancias) == 1

        # La distancia z debe corresponder con la w seleccionada
        problem += z[c1, c2] == pl.lpSum(dist * w[c1, c2, dist]
                                        for dist in distancias)

# ==== SOLUCIÓN ====
solver = pl.PULP_CBC_CMD(
    threads=12,
    msg=1,
    timeLimit=900,  # 15 minutos
    gapRel=0.1,    # 10% de gap
    maxNodes=5000  # ~5-6x el nodo donde se encontró la primera solución
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

create_schedule_csv(problem.variables(), Td, "schedule2-v2.csv")
