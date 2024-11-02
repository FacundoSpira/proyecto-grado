import pulp as pl
from itertools import product

# PROBLEMA DE OPTIMIZACIÓN
problem = pl.LpProblem("Optimizacion_Calendario", pl.LpMinimize)

# CONJUNTOS
# D: Conjunto de días del calendario
D = [1, 2, 3, 4, 5]

# C: Conjunto de unidades curriculares
C = ["cDiv", "gal1", "cDivv", "gal2", "pye", "md1", "md2", "p1", "p2", "tProg"]

# T: Conjunto de turnos
T = [1, 2, 3]

# S: Conjunto de semestres. Cada semestre representa una altura de la carrera que la unidad curricular puede ser sugerida
S = [1, 2, 3, 4, 5]

# K: Conjunto de carreras
K = ["computacion"]

# SUG: Conjunto de triplas donde la unidad curricular c se sugiere en el semestre s para la carrera k
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
    ("tProg", 5, "computacion")
]

# PA: Conjunto de triplas donde la unidad curricular c se asigna en el dia d en el turno t
PA = []

# P: Conjunto de pares de unidades curriculares (uc) donde la uc 1 es previa de la uc 2
P = [
    ("cDiv", "cDivv"),
    ("gal1", "gal2"),
    ("cDivv", "pye"),
    ("gal2", "p1"),
]

# PARÁMETROS

# cp(d,t): es la capacidad total del día d en el turno t
cp = {
    (d, t): 70 for d, t in product(D, T)
}

# fac_cp: porcentaje que se decide usar de la capacidad
fac_cp = 1

# ins(c): es la cantidad de inscriptos en la unidad curricular c
ins = {
    "cDiv": 50,
    "gal1": 40,
    "cDivv": 30,
    "gal2": 20,
    "pye": 50,
    "md1": 30,
    "md2": 20,
    "p1": 15,
    "p2": 10,
    "tProg": 15
}

# co(c1, c2): es la cantidad de estudiantes incriptos en simultáneo en las unidades curriculares c1 y c2
co = {
    (c1, c2): 0 if c1 != c2 else ins[c1] for c1, c2 in product(C, C)
}

# FUNCIONES AUXILIARES

# dist(d1, d2): distancia entre los días d1 y d2 del conjunto de días en el calendario
def dist(d1, d2):
    return abs(d1 - d2)

# dist_sem(c1, c2): distancia en semestres entre las unidades curriculares c1 y c2
def dist_sem(c1, c2):
    return min([abs(s1 - s2) for s1, s2 in product([s for c, s, k in SUG if c == c1], [s for c, s, k in SUG if c == c2])])

x = pl.LpVariable.dicts("x", (C, D, T), cat=pl.LpBinary)

for c in C:
    problem += pl.lpSum(x[c][d][t] for d in D for t in T(d)) == 1, f"AsignacionUnica_{c}"

for d in D:
    for (c1, s, k) in SUG:
        for (c2, s2, k2) in SUG:
            if c1 != c2 and s == s2 and k == k2:
                problem += pl.lpSum(x[c1][d][t] + x[c2][d][t] for t in T(d)) <= 1, f"Dias_Distintos_{c1}_{c2}_Dia_{d}"

for d in D:
    for t in T(d):
        problem += pl.lpSum(ins[c] * x[c][d][t] for c in C) <= cp[d,t] * fac_cp, f"Capacidad_{d}_{t}"

for c,d,t in PA:
    problem += x[c][d][t] == 1, f"Pre_asignacion_{c}_{d}_{t}"

y = pl.LpVariable.dicts("y", (C, D, C, D), cat="Binary")

for c1, c2 in product(C, repeat=2):
    for d1, d2 in product(D, repeat=2):
        problem += y[c1][d1][c2][d2] <= pl.lpSum(x[c1][d1][t1]) for t1 in T), f"Restriccion_y_r1_{c1}_{d1}_{c2}_{d2}"

for c1, c2 in product(C, repeat=2):
    for d1, d2 in product(D, repeat=2):
        problem += y[c1][d1][c2][d2] <= pl.lpSum(x[c2][d2][t2]) for t2 in T), f"Restriccion_y_r2_{c1}_{d1}_{c2}_{d2}"

for c1, c2 in product(C, repeate=2):
    for d1, d2 in product(D, repeate=2):
        problem += y[c1][d1][c2][d2] >= pl.lpSum(X[c1][d1][t1] for t1 in T) + pl.lpSum(x[c2][d2][t2] for t2 in T) - 1, f"Restriccion_y_r3_{c1}_{d1}_{c2}_{d2}"
