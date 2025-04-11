from metrics import generate_metrics
import sys
import os

DATA_PATH = "data"
CASE_PATH = "casos/caso_2s1p"


if __name__ == "__main__":
    schedule_file = sys.argv[1] if len(sys.argv) > 1 else "ema_schedule_1s2p.csv"

    metrics = generate_metrics(
        schedule_file,
        f"{CASE_PATH}/coincidencia.csv",
        f"{DATA_PATH}/previas.csv",
        f"{CASE_PATH}/trayectoria_sugerida.csv",
    )

    print(metrics)

    # USED TO RE-RUN METRICS FOR OUTPUT_PARAMETERS
    # results_file = "results.csv"
    # with open(results_file, "w") as f:
    #     f.write("alpha,beta,m_curricula,m_coincidencia,m_estudiantes,m_previas\n")

    # files = os.listdir("output_parameters")

    # for file in files:
    #     alpha = file.split("_")[3].split(":")[1]
    #     beta = file.split("_")[4].split(":")[1][:-4]

    #     schedule_file = f"output_parameters/{file}"

    #     metrics = generate_metrics(
    #         schedule_file,
    #         f"{CASE_PATH}/coincidencia.csv",
    #         f"{DATA_PATH}/previas.csv",
    #         f"{CASE_PATH}/trayectoria_sugerida.csv",
    #     )

    #     with open(results_file, "a") as f:
    #         f.write(
    #             f"{alpha},{beta},{metrics['m_curricula']},{metrics['m_coincidencia']},{metrics['m_estudiantes']},{metrics['m_previas']}\n"
    #         )
