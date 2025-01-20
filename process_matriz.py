import pandas as pd

# Read the CSV file
df = pd.read_csv('matriz_concurrencia.csv')

# Create mapping of unique materials to codes
# Combine mat1/cod1 and mat2/cod2 pairs
mapping_df1 = pd.DataFrame({
    'materia': df['mat1'],
    'codigo': df['cod1']
}).drop_duplicates()

mapping_df2 = pd.DataFrame({
    'materia': df['mat2'],
    'codigo': df['cod2']
}).drop_duplicates()

# Combine and remove duplicates
mapping_df = pd.concat([mapping_df1, mapping_df2]).drop_duplicates()
mapping_df = mapping_df.sort_values('materia')

# Calculate average cantidad for each cod1-cod2 pair
avg_cantidad_df = df.groupby(['cod1', 'cod2'])['cantidad'].mean().reset_index()
avg_cantidad_df = avg_cantidad_df.sort_values(['cod1', 'cod2'])

# Save to CSV files
mapping_df.to_csv('materias_codigos.csv', index=False)
avg_cantidad_df.to_csv('promedio_concurrencia.csv', index=False)

print("Files created successfully:")
print("1. materias_codigos.csv - Mapping of materials to codes")
print("2. promedio_concurrencia.csv - Average cantidad for each code pair")
