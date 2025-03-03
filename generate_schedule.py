import csv


def generate_schedule_csv(variables, csv_name="schedule.csv"):
    # Nos quedamos solo con las variables x que valen 1.
    schedule_vars = {}
    for v in variables:
        if v.name.startswith("x_") and v.value() == 1.0:
            schedule_vars[v.name] = v.value()

    # Extraemos los días y turnos máximos de las variables
    max_day = 1
    max_turn = 1
    for var_name in schedule_vars:
        # Las variables tienen la forma x_<uc>_<dia>_<turno>
        parts = var_name.split("_")
        _, _, day, turn = parts
        max_day = max(max_day, int(day))
        max_turn = max(max_turn, int(turn))

    # Creamos un diccionario con la estructura de la tabla.
    schedule = {
        i: {j: [] for j in range(1, max_turn + 1)} for i in range(1, max_day + 1)
    }

    # Cargamos las descripciones de las unidades curriculares.
    uc_descriptions = {}
    with open("data/unidades_curriculares.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uc_descriptions[row["codigo"]] = row["descripcion"]

    # Procesamos cada una de las variables para agregarlas al schedule.
    for var_name in schedule_vars:
        parts = var_name.split("_")
        _, uc, day, turn = parts

        # Buscamos la descripción de la UC. Fallback al código si no se encuentra.
        uc_description = uc_descriptions.get(uc, uc)

        day = int(day)
        turn = int(turn)
        schedule[day][turn].append(uc_description)

    # Escribimos el archivo CSV.
    with open(csv_name, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Encabezado
        header = ["Día/Turno"] + [f"Turno {i}" for i in range(1, max_turn + 1)]
        writer.writerow(header)

        # Cuerpo principal
        for day in range(1, max_day + 1):
            row = [f"Día {day}"]

            # Procesamos cada turno
            for turn in range(1, max_turn + 1):
                cell = " & ".join(schedule[day][turn]) if schedule[day][turn] else ""
                row.append(cell)

            writer.writerow(row)
