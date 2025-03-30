import os
import csv


def load_csv(file_path):
    if os.path.exists(file_path):
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            return [row for row in reader]
    else:
        print(f"Warning: {file_path} not found.")
        return []


def get_course_code(course_name, codes_data, actual_courses_data):
    course_name = course_name.strip().lower()
    possible_codes = [
        row[1] for row in codes_data if row[0].strip().lower() == course_name
    ]

    if not possible_codes:
        return course_name  # No matching code found, keep original name

    # Check which codes exist in actual_courses.csv
    actual_codes = {row[1] for row in actual_courses_data}
    valid_codes = [code for code in possible_codes if code in actual_codes]

    return valid_codes[0] if valid_codes else possible_codes[0]


def update_schedule(schedule_file, codes_file, actual_courses_file):
    schedule_data = load_csv(schedule_file)
    codes_data = load_csv(codes_file)[1:]  # Skip header
    actual_courses_data = load_csv(actual_courses_file)[1:]  # Skip header

    if not schedule_data or not codes_data:
        print("Missing required files. Exiting.")
        return

    header = schedule_data[0]
    updated_rows = [header]

    for row in schedule_data[1:]:
        # Mantenemos la columna con el nombre del día
        updated_row = [row[0]]

        for cell in row[1:]:
            cell = cell.strip()

            if not cell:
                # No hay asignaciones en el turno, dejamos vacío
                updated_row.append(cell)
                continue

            courses = [course.strip() for course in cell.split(" & ")]

            # Agregamos el código de la unidad curricular
            updated_courses = [
                f"{course} ({get_course_code(course, codes_data, actual_courses_data)})"
                for course in courses
            ]
            formatted_cell = " & ".join(updated_courses)
            updated_row.append(formatted_cell)

        updated_rows.append(updated_row)

    output_file = os.path.basename(schedule_file)
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(updated_rows)


if __name__ == "__main__":
    update_schedule("ema_schedule.csv", "data/unidades_curriculares.csv", "casos/caso_lg/unidades_curriculares.csv")
