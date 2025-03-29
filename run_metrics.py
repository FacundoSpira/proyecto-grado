from metrics import generate_metrics

DATA_PATH = "data"
CASE_PATH = "casos/caso_lg"

metrics = generate_metrics(
    # "output/schedule_8hs-alpha:1-beta:1-nuevas-restricciones.csv",
    # "output/schedule_nuevo-15m-alpha:1-beta:1.csv",
    # "output/schedule_nuevo-15m-alpha:1-beta:0.csv",
    "ema_schedule.csv",
    f"{DATA_PATH}/unidades_curriculares.csv",
    f"{CASE_PATH}/coincidencia.csv",
    f"{DATA_PATH}/previas.csv",
    f"{CASE_PATH}/trayectoria_sugerida.csv",
)

print(metrics)
