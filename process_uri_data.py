import pandas as pd

# region Leer los archivos CSV
df_concurrencia = pd.read_csv(
    "data/matriz_concurrencia.csv", dtype={"nom_periodo": str}
)
df_inscripciones = pd.read_csv("data/inscritos_por_uc_anio.csv")
# endregion

# region Crear mapeo de uc únicas a códigos
mapping_df1 = pd.DataFrame(
    {"descripcion": df_concurrencia["mat1"], "codigo": df_concurrencia["cod1"]}
).drop_duplicates()

mapping_df2 = pd.DataFrame(
    {"descripcion": df_concurrencia["mat2"], "codigo": df_concurrencia["cod2"]}
).drop_duplicates()

# Combinar y eliminar duplicados
mapping_df = (
    pd.concat([mapping_df1, mapping_df2]).drop_duplicates().sort_values("descripcion")
)
# endregion

# region Procesar matriz de concurrencia

# Extraer el semestre directamente del último dígito del período
df_concurrencia["semestre"] = df_concurrencia["nom_periodo"].str[-1].astype(int)

# Calcular cantidad promedio para cada par cod1-cod2 por semestre
avg_concurrencia = (
    df_concurrencia.groupby(["cod1", "cod2", "semestre"])["cantidad"]
    .mean()
    .reset_index()
)

# Crear DataFrames separados para cada semestre de concurrencia con formato coincidencia.csv
avg_conc_sem1 = (
    avg_concurrencia[avg_concurrencia["semestre"] == 1]
    .rename(columns={"cod1": "uc_1", "cod2": "uc_2", "cantidad": "coincidencia"})
    .drop("semestre", axis=1)
)
avg_conc_sem2 = (
    avg_concurrencia[avg_concurrencia["semestre"] == 2]
    .rename(columns={"cod1": "uc_1", "cod2": "uc_2", "cantidad": "coincidencia"})
    .drop("semestre", axis=1)
)
# endregion

# region Procesar inscripciones por semestre
# Convertir fecha_inicio a datetime
df_inscripciones["fecha_inicio"] = pd.to_datetime(df_inscripciones["fecha_inicio"])

# Agregar columna de semestre (1 o 2)
df_inscripciones["semestre"] = df_inscripciones["fecha_inicio"].dt.month.map(
    lambda x: 1 if x <= 6 else 2
)

# Calcular promedio por código y semestre
avg_inscripciones = (
    df_inscripciones.groupby(["codenservicio_mat", "semestre"])["cantidad"]
    .mean()
    .reset_index()
)

# Crear DataFrames separados para cada semestre de inscripciones con formato inscriptos.csv
avg_insc_sem1 = (
    avg_inscripciones[avg_inscripciones["semestre"] == 1]
    .rename(columns={"codenservicio_mat": "uc", "cantidad": "inscriptos"})
    .drop("semestre", axis=1)
)
avg_insc_sem2 = (
    avg_inscripciones[avg_inscripciones["semestre"] == 2]
    .rename(columns={"codenservicio_mat": "uc", "cantidad": "inscriptos"})
    .drop("semestre", axis=1)
)

# Redondear valores de inscriptos a enteros
avg_insc_sem1["inscriptos"] = avg_insc_sem1["inscriptos"].round().astype(int)
avg_insc_sem2["inscriptos"] = avg_insc_sem2["inscriptos"].round().astype(int)

# endregion

# region Guardar archivos por semestre
mapping_df.to_csv("data/unidades_curriculares.csv", index=False)
avg_conc_sem1.to_csv("data/coincidencia_sem1.csv", index=False)
avg_conc_sem2.to_csv("data/coincidencia_sem2.csv", index=False)
avg_insc_sem1.to_csv("data/inscriptos_sem1.csv", index=False)
avg_insc_sem2.to_csv("data/inscriptos_sem2.csv", index=False)

print("Archivos creados exitosamente:")
print("1. unidades_curriculares.csv - Mapeo de materias a códigos")
print("2. coincidencia_sem1.csv - Promedio de concurrencia del primer semestre")
print("3. coincidencia_sem2.csv - Promedio de concurrencia del segundo semestre")
print("4. inscriptos_sem1.csv - Promedio de inscripciones del primer semestre")
print("5. inscriptos_sem2.csv - Promedio de inscripciones del segundo semestre")
# endregion
