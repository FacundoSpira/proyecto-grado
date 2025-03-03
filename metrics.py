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


def load_previas(file_name):
    previas = []
    with open(file_name, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            previas.append((row[0], row[1]))
    return previas


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


def load_calendar_in_turns(calendar_file):
    calendar = {}

    with open(calendar_file, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)

        for row in reader:
            day = int(row[0].split(" ")[1])
            calendar[day] = {}

            for turn_idx in range(1, len(headers)):
                if turn_idx < len(row) and row[turn_idx].strip():
                    courses = [course.strip() for course in row[turn_idx].split(",")]
                else:
                    courses = []

                calendar[day][turn_idx] = courses

    return calendar


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
    inscripts_csv_name,
    capacity_csv_name,
    factor_cp,
):
    metrics = {}
    metrics["coherencia_curricular"] = compute_curriculum_consistency_metric(
        calendar_csv_name, uc_csv_name, suggested_csv_name
    )
    metrics["coincidencia_promedio"] = generate_weighted_average_for_coincidence_metric(
        calendar_csv_name, uc_csv_name, coincidences_csv_name
    )
    metrics["capacidad_utilizada"] = compute_average_capacity_utilization(
        calendar_csv_name, uc_csv_name, inscripts_csv_name, capacity_csv_name, factor_cp
    )
    metrics["estudiantes_afectados"] = generate_affected_student_metric(
        calendar_csv_name, uc_csv_name, coincidences_csv_name
    )
    metrics["coherencia_previas"] = compute_previas_consistency_metric(
        calendar_csv_name, uc_csv_name, previatures_csv_name
    )

    return metrics


def generate_weighted_average_for_coincidence_metric(
    calendar_name, courses_file_name, coincidence_file_name
):
    calendar = load_calendar(calendar_name)
    course_dict = load_course_codes(courses_file_name)
    coincidence_dict = load_coincidences(coincidence_file_name)

    course_days = {}
    for day_label, courses in calendar.items():
        day_number = int(day_label.split()[-1])
        for course in courses:
            if course in course_dict:
                course_code = course_dict[course]
                course_days[course_code] = day_number

    weighted_distance_sum = 0.0
    total_coincidence_sum = 0.0
    weighted_square_distance_sum = 0.0

    for (c1, c2), coincidence in coincidence_dict.items():
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


def generate_affected_student_metric(
    calendar_name, courses_file_name, coincidence_file_name
):
    calendar = load_calendar(calendar_name)
    course_dict = load_course_codes(courses_file_name)
    coincidence_dict = load_coincidences(coincidence_file_name)

    calendar_codes = {
        day: {course_dict[course] for course in courses if course in course_dict}
        for day, courses in calendar.items()
    }

    total_conflicts = 0.0
    days = sorted(calendar_codes.keys(), key=lambda x: int(x.split()[-1]))

    for i, day in enumerate(days):
        courses_today = calendar_codes[day]

        for c1 in courses_today:
            for c2 in courses_today:
                if c1 < c2:
                    total_conflicts += coincidence_dict.get((c1, c2), 0.0)

        if i < len(days) - 1:
            next_day = days[i + 1]
            courses_next_day = calendar_codes[next_day]

            for c1 in courses_today:
                for c2 in courses_next_day:
                    total_conflicts += coincidence_dict.get((c1, c2), 0.0)

    return total_conflicts


def compute_average_capacity_utilization(
    calendar_name, courses_file_name, enrollment_file, capacity_file, capacity_factor
):
    calendar = load_calendar_in_turns(calendar_name)
    course_dict = load_course_codes(courses_file_name)
    enrollments = load_enrollments(enrollment_file)
    capacities = load_capacities(capacity_file)

    total_days = len(calendar)
    if total_days == 0:
        return 0.0

    daily_utilization = []

    for day, turns in calendar.items():
        students_scheduled = sum(
            enrollments.get(course_dict[course], 0)
            for turn_courses in turns.values()
            for course in turn_courses
            if course in course_dict
        )

        total_capacity = sum(
            capacity_factor * capacities.get((day, turn), 0) for turn in turns.keys()
        )

        if total_capacity > 0:
            daily_utilization.append(students_scheduled / total_capacity)
        else:
            daily_utilization.append(0.0)

    return sum(daily_utilization) / total_days if total_days > 0 else 0.0


def compute_curriculum_consistency_metric(
    calendar_name, courses_file_name, suggested_file
):
    calendar = load_calendar(calendar_name)
    course_dict = load_course_codes(courses_file_name)
    suggested_courses = load_suggested_courses(suggested_file)

    course_days = {
        course_dict[c]: int(day.split()[-1])
        for day, courses in calendar.items()
        for c in courses
        if c in course_dict
    }

    distances = []
    pairs_count = 0

    for c1, s, k in suggested_courses:
        for c2, s2, k2 in suggested_courses:
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


def compute_previas_consistency_metric(calendar_name, courses_file_name, previas_file):
    calendar = load_calendar(calendar_name)
    course_dict = load_course_codes(courses_file_name)
    previas = load_previas(previas_file)

    course_days = {
        course_dict[c]: int(day.split()[-1])
        for day, courses in calendar.items()
        for c in courses
        if c in course_dict
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
