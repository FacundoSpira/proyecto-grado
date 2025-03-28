import yaml
import csv

def extract_subject_codes(operands, subject_code):
    results = []

    if not isinstance(operands, list):
        operands = [operands]

    for operand in operands:
        if isinstance(operand, dict):
            if operand.get('type') == 'subject':
                # Add the relationship between the main subject and its prerequisite
                results.append((subject_code, operand.get('subject_needed_code')))
            elif operand.get('type') == 'logical':
                # Recursively process nested logical operators
                if 'operands' in operand:
                    results.extend(extract_subject_codes(operand['operands'], subject_code))

    return results

def convert_yaml_to_csv(yaml_file, csv_file):
    # Leer el archivo previas.yml
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Extraer todas las relaciones de códigos de asignaturas
    relationships = []
    for item in data:
        if isinstance(item, dict) and 'subject_code' in item and 'operands' in item:
            relationships.extend(extract_subject_codes(item['operands'], item['subject_code']))

    # Escribir a CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['uc', 'uc_requerida'])  # Títulos
        for rel in relationships:
            if rel[0] and rel[1]:  # Solo escribir si ambos códigos existen
                writer.writerow(rel)


# Convertir el archivo previas.yml a CSV
convert_yaml_to_csv("data/previas.yml", "data/previas.csv")
