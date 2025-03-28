from metrics import generate_metrics
import os
import csv
import re

def extract_info_from_filename(filename):
    # Extract alpha value
    alpha_match = re.search(r'alpha_(\d+(?:\.\d+)?)', filename)
    alpha = float(alpha_match.group(1)) if alpha_match else 0.0

    # Extract time limit
    time_limit_match = re.search(r'timelimit_(\d+)', filename)
    time_limit = int(time_limit_match.group(1)) if time_limit_match else 0

    return alpha, time_limit

def run_metrics_for_file(calendar_file, alpha, factor_cp=1):
    # Define paths for caso_lg (large case)
    case_name = "caso_lg"  # Hardcoded to large case
    uc_csv_name = f"data/unidades_curriculares.csv"
    coincidences_csv_name = f"casos/{case_name}/coincidencia.csv"
    previatures_csv_name = f"data/previas.csv"
    suggested_csv_name = f"casos/{case_name}/trayectoria_sugerida.csv"
    inscripts_csv_name = f"casos/{case_name}/inscriptos.csv"
    capacity_csv_name = f"casos/{case_name}/capacidad.csv"

    # Generate metrics
    metrics = generate_metrics(
        calendar_file,
        uc_csv_name,
        coincidences_csv_name,
        previatures_csv_name,
        suggested_csv_name,
        inscripts_csv_name,
        capacity_csv_name,
        0.5,
        factor_cp
    )

    return metrics

def main():
    output_dir = "output"
    output_file = "metrics_results.csv"
    results = []

    # Get all CSV files in the output directory
    for filename in os.listdir(output_dir):
        if filename.endswith(".csv") and filename.startswith("schedule_"):
            full_path = os.path.join(output_dir, filename)

            # Extract information from filename
            alpha, time_limit = extract_info_from_filename(filename)

            print(f"Processing {filename}...")

            try:
                # Run metrics for this file
                metrics = run_metrics_for_file(full_path, alpha)

                # Add results to our list
                result = {
                    "alpha": alpha,
                    "time_limit": time_limit,
                    **metrics
                }
                results.append(result)
                print(f"Successfully processed {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

    # Write results to CSV
    if results:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Get all field names (headers)
            fieldnames = ["alpha"]
            for result in results:
                for key in result.keys():
                    if key not in fieldnames:
                        fieldnames.append(key)

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"Results written to {output_file}")
    else:
        print("No results to write")

if __name__ == "__main__":
    main()
