from metrics import generate_metrics

DATA_PATH = "data"
CASE_PATH = "casos/caso_lg"

metrics = generate_metrics(
    "output/schedule_2025.02.16_21:57:02.csv",
    f"{DATA_PATH}/unidades_curriculares.csv",
    f"{CASE_PATH}/coincidencia.csv",
    f"{DATA_PATH}/previas.csv",
    f"{CASE_PATH}/trayectoria_sugerida.csv",
)

print(metrics)
