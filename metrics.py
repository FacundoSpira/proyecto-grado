import math
import csv

ALPHA = 0.5


# region FUNCIONES PARA CARGAR DATOS
def load_course_codes(filename):
    course_dict = {}
    with open(filename, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            name, code = row
            course_dict[name] = code
    return course_dict


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
    calendar = {}

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
                    courses.update(course.strip() for course in cell.split(","))

            calendar[day] = courses

    return calendar


# endregion


def generate_metrics(
    calendar_csv_name,
    uc_csv_name,
    coincidences_csv_name,
    previatures_csv_name,
    suggested_csv_name,
):
    calendar = load_calendar(calendar_csv_name)
    uc_codes = load_course_codes(uc_csv_name)
    coincidences = load_coincidences(coincidences_csv_name)
    previatures = load_previatures(previatures_csv_name)
    suggested_uc = load_suggested_courses(suggested_csv_name)

    metrics = {}
    metrics["m_curricula"] = compute_m_curricula(
        calendar=calendar,
        uc_codes=uc_codes,
        suggested_uc=suggested_uc,
    )
    metrics["m_coincidencia"] = compute_m_coincidencia(
        calendar=calendar,
        uc_codes=uc_codes,
        coincidences=coincidences,
    )
    metrics["m_estudiantes"] = compute_m_estudiantes(
        calendar=calendar,
        uc_codes=uc_codes,
        coincidences=coincidences,
    )
    metrics["m_previas"] = compute_m_previas(
        calendar=calendar,
        uc_codes=uc_codes,
        previas=previatures,
    )

    return metrics


def compute_m_coincidencia(calendar, uc_codes, coincidences):
    course_days = {}
    for day_label, courses in calendar.items():
        day_number = int(day_label.split()[-1])
        for course in courses:
            if course in uc_codes:
                course_code = uc_codes[course]
                course_days[course_code] = day_number

    weighted_distance_sum = 0.0
    total_coincidence_sum = 0.0
    weighted_square_distance_sum = 0.0

    for (c1, c2), coincidence in coincidences.items():
        if c1 in course_days and c2 in course_days:
            z_distance = abs(course_days[c1] - course_days[c2])
            weighted_distance_sum += coincidence * z_distance
            weighted_square_distance_sum += coincidence * (z_distance**2)
            total_coincidence_sum += coincidence

    if total_coincidence_sum == 0:
        return 0.0

    z_bar = weighted_distance_sum / total_coincidence_sum
    variance = (weighted_square_distance_sum / total_coincidence_sum) - (z_bar**2)
    sigma = variance**0.5 if variance > 0 else 0.0

    metric_previas = z_bar * (1 - ALPHA * (sigma / z_bar)) if z_bar > 0 else 0.0

    return metric_previas


def compute_m_estudiantes(calendar, uc_codes, coincidences):
    calendar_codes = {
        day: {uc_codes[course] for course in courses if course in uc_codes}
        for day, courses in calendar.items()
    }

    total_conflicts = 0.0
    days = sorted(calendar_codes.keys(), key=lambda x: int(x.split()[-1]))

    for i, day in enumerate(days):
        courses_today = calendar_codes[day]

        for c1 in courses_today:
            for c2 in courses_today:
                if c1 < c2:
                    total_conflicts += coincidences.get((c1, c2), 0.0)

        if i < len(days) - 1:
            next_day = days[i + 1]
            courses_next_day = calendar_codes[next_day]

            for c1 in courses_today:
                for c2 in courses_next_day:
                    total_conflicts += coincidences.get((c1, c2), 0.0)

    return total_conflicts


def compute_m_curricula(calendar, uc_codes, suggested_uc):
    course_days = {
        uc_codes[c]: int(day.split()[-1])
        for day, courses in calendar.items()
        for c in courses
        if c in uc_codes
    }

    distances = []
    pairs_count = 0

    for c1, s, k in suggested_uc:
        for c2, s2, k2 in suggested_uc:
            if (
                s == s2
                and k == k2
                and c1 != c2
                and c1 in course_days
                and c2 in course_days
            ):
                z_distance = abs(course_days[c1] - course_days[c2])
                distances.append(z_distance)
                pairs_count += 1

    if pairs_count == 0:
        return 0.0

    z_curriculum = sum(distances) / pairs_count

    variance = sum((z - z_curriculum) ** 2 for z in distances) / pairs_count
    sigma_curriculum = math.sqrt(variance)

    m_curriculum = (
        z_curriculum * (1 - ALPHA * (sigma_curriculum / z_curriculum))
        if z_curriculum > 0
        else 0.0
    )

    return m_curriculum


def compute_m_previas(calendar, uc_codes, previas):
    course_days = {
        uc_codes[c]: int(day.split()[-1])
        for day, courses in calendar.items()
        for c in courses
        if c in uc_codes
    }

    distances = []
    pairs_count = 0

    for c1, c2 in previas:
        if c1 in course_days and c2 in course_days:
            z_distance = abs(course_days[c1] - course_days[c2])
            distances.append(z_distance)
            pairs_count += 1

    if pairs_count == 0:
        return 0.0

    z_previas = sum(distances) / pairs_count
    variance = sum((z - z_previas) ** 2 for z in distances) / pairs_count
    sigma_previas = math.sqrt(variance)

    m_previas = (
        z_previas * (1 + ALPHA * (sigma_previas / z_previas)) if z_previas > 0 else 0.0
    )

    return m_previas
