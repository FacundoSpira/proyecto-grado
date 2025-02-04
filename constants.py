MINUTES = 60


# Definición de un Enum para los diferentes solvers soportados
class Solver:
    CPLEX_CMD = "CPLEX_CMD"
    GUROBI_CMD = "GUROBI_CMD"
    PULP_CBC_CMD = "PULP_CBC_CMD"


# Definición de un Enum para los diferentes casos soportados
class Case:
    small = "casos/caso_sm"
    medium = "casos/caso_md"
    large = "casos/caso_lg"
