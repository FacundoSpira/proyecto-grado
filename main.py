from solve import solve_model, Solver
from generate_schedule import generate_schedule_csv


if __name__ == "__main__":
    value, time, variables = solve_model(
        "caso2", {"solver": Solver.GUROBI_CMD, "gapRel": 0.1, "maxNodes": 5000}
    )

    print(f"Valor óptimo de la función objetivo: {value}")
    print(f"Tiempo de ejecución: {time:.2f} segundos")
    generate_schedule_csv(variables, "schedule.csv")
