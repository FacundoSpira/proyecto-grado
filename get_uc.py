import pandas as pd

def extract_day_names(file_path):
    """
    Extract all unique names under 'Día' columns from the given CSV file.

    Args:
        file_path (str): Path to the CSV file

    Returns:
        list: Sorted list of unique names
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        print(df.columns)

        # Get columns containing "Día" in their name
        dia_columns = [col for col in df.columns if 'Día' in str(col)]

        # Create a set to store unique names
        nombres_unicos = set()

        # Iterate over day columns
        for col in dia_columns:
            # Get all non-null values from the column
            valores = df[col].dropna().tolist()
            # Add values to the set
            nombres_unicos.update(valores)

        # Convert set to sorted list
        return sorted(list(nombres_unicos))

    except Exception as e:
        print(f"Error processing file: {e}")
        return []

def main():
    file_path = '/Users/florenciacarle/Downloads/Copia de 1eros sem impar .xlsx - Sheet1.csv'
    nombres = extract_day_names(file_path)

    print("Nombres encontrados bajo columnas 'Día':")
    for nombre in nombres:
        print(nombre)

if __name__ == "__main__":
    main()

