from metrics import generate_metrics
import sys

DATA_PATH = "data"
CASE_PATH = "casos/caso_lg"


if __name__ == "__main__":
    schedule_file = sys.argv[1] if len(sys.argv) > 1 else "ema_schedule.csv"

    metrics = generate_metrics(
        schedule_file,
        f"{DATA_PATH}/unidades_curriculares.csv",
        f"{CASE_PATH}/coincidencia.csv",
        f"{DATA_PATH}/previas.csv",
        f"{CASE_PATH}/trayectoria_sugerida.csv",
    )

    print(metrics)
