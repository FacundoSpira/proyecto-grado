from solve import solve_model
from constants import Solver, Case
from generate_schedule import generate_schedule_csv
from datetime import datetime

if __name__ == "__main__":
    value, time, variables = solve_model(
        Case.large,
        {
            "solver": Solver.GUROBI_CMD,
            "gapRel": 0.05,
        },
    )

    print(f"Valor óptimo de la función objetivo: {value}")
    print(f"Tiempo de ejecución: {time:.2f} segundos")
    timestamp = datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
    generate_schedule_csv(variables, f"output/schedule_{timestamp}.csv")
