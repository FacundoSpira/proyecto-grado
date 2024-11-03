import csv


def create_schedule_csv(variables, turns, csv_name="schedule.csv"):
    # Nos quedamos solo con las variables x que valen 1.
    schedule_vars = {}
    for v in variables:
        if v.name.startswith("x_") and v.value() == 1.0:
            schedule_vars[v.name] = v.value()

    # Creamos un diccionario con la estructura de la tabla.
    max_day = max(turns.keys())
    max_turn = max(max(turn_list) for turn_list in turns.values())
    schedule = {
        i: {j: [] for j in range(1, max_turn + 1)} for i in range(1, max_day + 1)
    }

    # Procesamos cada una de las variables para agregarlas al schedule.
    for var_name in schedule_vars:
        parts = var_name.split("_")
        _, course, day, turn = parts
        day = int(day)
        turn = int(turn)
        schedule[day][turn].append(course)

    # Escribimos el archivo CSV.
    with open(csv_name, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Encabezado
        header = ["Día/Turno"] + [f"Turno {i}" for i in range(1, max_turn + 1)]
        writer.writerow(header)

        # Cuerpo principal
        for day in range(1, max_day + 1):
            row = [f"Día {day}"]

            turns_list = turns[day] if day in turns else None

            # Si el día no está en la lista, deshabilitamos todos los turnos.
            if turns_list is None:
                row += ["-" for _ in range(max_turn)]
                writer.writerow(row)
                continue

            # Si el día está en la lista, procesamos cada turno.
            for turn in range(1, max_turn + 1):
                if turn in turns_list:
                    cell = ", ".join(schedule[day][turn]) if schedule[day][turn] else ""
                else:
                    cell = "-"  # Marca turno deshabilitado

                row.append(cell)

            writer.writerow(row)
