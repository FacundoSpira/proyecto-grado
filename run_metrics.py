from metrics import generate_metrics

Metrics = generate_metrics("output/main-test-15-gurobi-1.csv", "data/unidades_curriculares.csv", "casos/caso_lg/coincidencia.csv", "data/previas.csv", "casos/caso_lg/trayectoria_sugerida.csv", "casos/caso_lg/inscriptos.csv", "casos/caso_lg/capacidad.csv", 0.5, 1)

print(Metrics)
