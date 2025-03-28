from con_turnos.solve import solve_model as solve_model_con_turnos
from sin_turnos.solve import solve_model as solve_model_sin_turnos
from constants import Solver, Case, Weight
from generate_schedule import generate_schedule_csv
from datetime import datetime
import os

def run_model(model_name, solve_func, case, solver, alpha):
    print(f"\n{'='*80}")
    print(f"Ejecutando {model_name} para caso: {case}, solver: {solver}, alpha: {alpha}")
    print(f"{'='*80}")

    start_time = datetime.now()

    # Llamar a la función de resolución con alpha
    value, time, status, variables = solve_func(case, solver, alpha)

    print("Status:", status)

    if status != "Optimal":
        print(f"Warning: El problema no tiene solución óptima. Status: {status}")
        return

    print(f"Valor óptimo de la función objetivo: {value}")
    print(f"Tiempo de ejecución: {time:.2f} segundos")
    print(f"                     {time/60:.2f} minutos")

    # Crear directorio de salida si no existe
    os.makedirs("output", exist_ok=True)

    # Generar timestamp para nombres de archivo únicos
    timestamp = datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
    filename = f"output/schedule_{model_name}_{case.split('/')[-1]}_alpha_{alpha}_{timestamp}.csv"

    generate_schedule_csv(variables, filename)
    print(f"Schedule saved to: {filename}")

if __name__ == "__main__":
    # Definir qué solver usar
    solver = Solver.GUROBI_CMD

    # Definir valores de alpha a probar
    alpha_values = [Weight.NO_WEIGHT, Weight.WEIGHT_1, Weight.WEIGHT_2, Weight.WEIGHT_3, Weight.WEIGHT_4]

    # Ejecutar ambos modelos para cada caso y valor de alpha

    for alpha in alpha_values:
        print("con turnos", alpha)
        print("sin turnos", alpha)
        # # Ejecutar modelo con_turnos con alpha
        # run_model("con_turnos", solve_model_con_turnos, Case.large, solver, alpha)

        # # Ejecutar modelo sin_turnos con alpha
        # run_model("sin_turnos", solve_model_sin_turnos, Case.large, solver, alpha)

    print("\nTodos los modelos completados!")
