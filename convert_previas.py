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
    # Read YAML file
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Extract all subject code relationships
    relationships = []
    for item in data:
        if isinstance(item, dict) and 'subject_code' in item and 'operands' in item:
            relationships.extend(extract_subject_codes(item['operands'], item['subject_code']))

    # Write to CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['uc', 'uc_requerida'])  # Header
        for rel in relationships:
            if rel[0] and rel[1]:  # Only write if both codes exist
                writer.writerow(rel)

# Convert the file
convert_yaml_to_csv('previas.yml', 'previas.csv')
