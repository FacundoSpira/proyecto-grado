from solve import solve_model
from constants import Solver, Case, Weight
from generate_schedule import generate_schedule_csv
from datetime import datetime
import os

def run_solver(solver_name, case, alpha):
    print(f"\n{'='*50}")
    print(f"Ejecutando con solver: {solver_name}")
    print(f"Caso: {case}")
    print(f"Alpha: {alpha}")
    print(f"{'='*50}")

    try:
        value, time, status, variables = solve_model(case, solver_name, alpha, 60)

        print(f"Estado: {status}")
        print(f"Valor óptimo: {value}")
        print(f"Tiempo de ejecución: {time:.2f} segundos ({time/60:.2f} minutos)")

        if status == "Optimal" or status == "Feasible":
            timestamp = datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            output_file = f"{output_dir}/schedule_{solver_name}_{timestamp}.csv"
            generate_schedule_csv(variables, output_file)
            print(f"Calendario guardado en: {output_file}")

        return {
            "solver": solver_name,
            "status": status,
            "value": value,
            "time": time
        }
    except Exception as e:
        print(f"Error al ejecutar el solver {solver_name}: {str(e)}")
        return {
            "solver": solver_name,
            "status": "Error",
            "value": None,
            "time": None,
            "error": str(e)
        }

if __name__ == "__main__":
    # Definir el caso y el valor de alpha a utilizar
    case = Case.large
    alpha = Weight.WEIGHT_2  # Puedes cambiar esto a cualquier valor de peso

    # Lista de todos los solvers disponibles
    solvers = [Solver.CPLEX_CMD, Solver.GUROBI_CMD, Solver.PULP_CBC_CMD]

    # Ejecutar cada solver y recopilar resultados
    results = []
    for solver in solvers:
        result = run_solver(solver, case, alpha)
        results.append(result)

    # Imprimir resumen de resultados
    print("\n\n" + "="*70)
    print("RESUMEN DE RESULTADOS")
    print("="*70)
    print(f"{'Solver':<15} | {'Estado':<10} | {'Valor Objetivo':<20} | {'Tiempo (segundos)':<15}")
    print("-"*70)

    for result in results:
        solver = result["solver"]
        status = result["status"]
        value = result["value"] if result["value"] is not None else "N/A"
        time = f"{result['time']:.2f}" if result["time"] is not None else "N/A"

        print(f"{solver:<15} | {status:<10} | {value:<20} | {time:<15}")
