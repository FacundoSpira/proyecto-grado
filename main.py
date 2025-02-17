from solve import solve_model
from constants import Solver, Case
from generate_schedule import generate_schedule_csv
from datetime import datetime

if __name__ == "__main__":
    value, time, status, variables = solve_model(Case.large, Solver.GUROBI_CMD)

    print("Status:", status)

    if status != "Optimal":
        raise Exception(f"El problema no tiene solución óptima. Status: {status}")

    for v in variables:
        print(v.name, "=", v.varValue)

    print(f"Valor óptimo de la función objetivo: {value}")

    print(f"Tiempo de ejecución: {time:.2f} segundos")
    print(f"                     {time/60:.2f} minutos")

    timestamp = datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
    generate_schedule_csv(variables, f"output/schedule_{timestamp}.csv")
