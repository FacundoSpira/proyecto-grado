import pandas as pd

# Leer el archivo CSV
df = pd.read_csv("data/matriz_concurrencia.csv")

# Crear mapeo de materias únicas a códigos
# Combinar pares mat1/cod1 y mat2/cod2
mapping_df1 = pd.DataFrame(
    {"materia": df["mat1"], "codigo": df["cod1"]}
).drop_duplicates()

mapping_df2 = pd.DataFrame(
    {"materia": df["mat2"], "codigo": df["cod2"]}
).drop_duplicates()

# Combinar y eliminar duplicados
mapping_df = pd.concat([mapping_df1, mapping_df2]).drop_duplicates()
mapping_df = mapping_df.sort_values("materia")

# Calcular cantidad promedio para cada par cod1-cod2
avg_cantidad_df = df.groupby(["cod1", "cod2"])["cantidad"].mean().reset_index()
avg_cantidad_df = avg_cantidad_df.sort_values(["cod1", "cod2"])

# Guardar en archivos CSV
mapping_df.to_csv("data/unidades_curriculares.csv", index=False)
avg_cantidad_df.to_csv("data/promedio_concurrencia.csv", index=False)

print("Archivos creados exitosamente:")
print("1. materias_codigos.csv - Mapeo de materias a códigos")
print("2. promedio_concurrencia.csv - Promedio de cantidad para cada par de códigos")
