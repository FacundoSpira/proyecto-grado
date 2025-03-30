import math
import csv
import re
from itertools import combinations

ALPHA = 0.5

def load_enrollments(enrollment_file):
    enrollments = {}
    with open(enrollment_file, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            course_code, num_students = row
            enrollments[course_code] = int(num_students)
    return enrollments


def load_capacities(capacity_file):
    capacities = {}
    with open(capacity_file, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            day, turn, capacity = row
            capacities[(int(day), int(turn))] = int(capacity)
    return capacities


def load_previatures(file_name):
    previatures = []
    with open(file_name, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            previatures.append((row[0], row[1]))
    return previatures


def load_coincidences(filename):
    coincidence_dict = {}
    with open(filename, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            uc1, uc2, coincidence = row[0], row[1], float(row[2])
            coincidence_dict[(uc1, uc2)] = coincidence
            coincidence_dict[(uc2, uc1)] = coincidence
    return coincidence_dict


def load_suggested_courses(suggested_file):
    suggested_courses = set()
    with open(suggested_file, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            course, semester, career = row
            suggested_courses.add((course, int(semester), career))
    return suggested_courses


def load_calendar(filename):
    uc_day = {}
    calendar = {}
    codes = {}
    reader = csv.reader(filename)

    with open(filename, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader, None)

        for row in reader:
            if not row:
                continue

            day = row[0].strip()
            courses = set()

            for cell in row[1:]:
                if cell.strip():
                    courses.update(course.strip() for course in cell.split("&"))

                    for course in courses:
                        match = re.match(r"(.+?) \((\d+)\)$", course)
                        if match:
                            codes[match.group(1)] = match.group(2)

            calendar[day] = courses

    for day_label, courses in calendar.items():
        day_number = int(day_label.split()[-1])
        for course in courses:
            match = re.match(r"(.+?) \((\d+)\)$", course)
            if match:
                course_name = match.group(1)

                if course_name in codes:
                    course_code = codes[course_name]
                    uc_day[course_code] = day_number

    return uc_day

# endregion


def generate_metrics(
    calendar_csv_name,
    coincidences_csv_name,
    previatures_csv_name,
    suggested_csv_name,
):
    uc_day = load_calendar(calendar_csv_name)
    coincidences = load_coincidences(coincidences_csv_name)
    previatures = load_previatures(previatures_csv_name)
    suggested_uc = load_suggested_courses(suggested_csv_name)

    metrics = {}
    metrics["m_curricula"] = compute_m_curricula(
        uc_day=uc_day,
        suggested_uc=suggested_uc,
    )
    metrics["m_coincidencia"] = compute_m_coincidencia(
        uc_day=uc_day,
        coincidences=coincidences,
    )
    metrics["m_estudiantes"] = compute_m_estudiantes(
        uc_day=uc_day,
        coincidences=coincidences,
    )
    metrics["m_previas"] = compute_m_previas(
        uc_day=uc_day,
        previatures=previatures,
    )

    return metrics


def compute_m_coincidencia(uc_day, coincidences):
    # Generamos un conjunto, con los pares de cursos.
    PARES_CURSOS = list(combinations(uc_day.keys(), 2))

    total_coincidences_sum = sum(
        coincidences.get((c1, c2), 0.0) for c1, c2 in PARES_CURSOS
    )

    weighted_distance_sum = sum(
        coincidences.get((c1, c2), 0.0) * abs(uc_day[c1] - uc_day[c2])
        for c1, c2 in PARES_CURSOS
    )

    z_bar = weighted_distance_sum / total_coincidences_sum

    sigma_numerator = sum(
        coincidences.get((c1, c2), 0.0) * (abs(uc_day[c1] - uc_day[c2]) - z_bar) ** 2
        for c1, c2 in PARES_CURSOS
    )
    sigma = math.sqrt(sigma_numerator / total_coincidences_sum)

    metric_coincidencia = z_bar * (1 - ALPHA * (sigma / z_bar))

    return metric_coincidencia


def compute_m_estudiantes(uc_day, coincidences):
    # Generamos un conjunto, con los pares de cursos.
    PARES_CURSOS = list(combinations(uc_day.keys(), 2))

    total_conflicts_sum = sum(
        coincidences.get((c1, c2), 0.0)
        for c1, c2 in PARES_CURSOS
        if abs(uc_day[c1] - uc_day[c2]) <= 1
    )

    return total_conflicts_sum


def compute_m_curricula(uc_day, suggested_uc):
    distances = []

    # Agrupar cursos por semestre y carrera
    semester_groups = {}
    for c, s, k in suggested_uc:
        # Solo considerar cursos que están en el calendario
        if c in uc_day:
            key = (s, k)
            if key not in semester_groups:
                semester_groups[key] = []

            semester_groups[key].append(c)

    # Para cada grupo (mismo semestre y carrera), calcular las distancias
    for courses in semester_groups.values():
        for c1, c2 in combinations(courses, 2):
            z_distance = abs(uc_day[c1] - uc_day[c2])
            distances.append(z_distance)

    if len(distances) == 0:
        return 0.0

    z_curriculum = sum(distances) / len(distances)

    variance = sum((z - z_curriculum) ** 2 for z in distances) / len(distances)
    sigma_curriculum = math.sqrt(variance)

    m_curriculum = z_curriculum * (1 - ALPHA * (sigma_curriculum / z_curriculum))

    return m_curriculum


def compute_m_previas(uc_day, previatures):
    # Calculamos las previas que existen en el calendario.
    PREVIAS = [
        (c1, c2) for c1, c2 in previatures if c1 != c2 and c1 in uc_day and c2 in uc_day
    ]

    P = len(PREVIAS)

    if P == 0:
        return 0.0

    distance_previatures_sum = sum(abs(uc_day[c1] - uc_day[c2]) for c1, c2 in PREVIAS)

    z_previas = distance_previatures_sum / P

    variance = (
        sum((abs(uc_day[c1] - uc_day[c2]) - z_previas) ** 2 for c1, c2 in PREVIAS) / P
    )
    sigma_previas = math.sqrt(variance)

    m_previas = (
        z_previas * (1 + ALPHA * (sigma_previas / z_previas)) if z_previas > 0 else 0.0
    )

    return m_previas
