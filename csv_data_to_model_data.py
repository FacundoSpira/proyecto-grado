import pandas as pd
import os
from itertools import combinations


def load_calendar_data(dir_name):
    """
    Carga los conjuntos y parámetros desde archivos CSV para el modelo de calendario
    de evaluaciones.

    Args:
        directorio_datos (str): Ruta al directorio que contiene los archivos CSV

    Returns:
        dict: Diccionario con todos los conjuntos y parámetros del modelo
    """

    def load_csv(name):
        file_path = os.path.join(dir_name, f"{name}.csv")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No se encontró el archivo {file_path}")

        return pd.read_csv(file_path)

    try:
        # ==== CONJUNTOS ====

        # Días del calendario
        D = sorted(list(load_csv("dias")["id"]))

        # Unidades curriculares
        C = list(load_csv("unidades_curriculares")["codigo"])

        # Turnos
        T = sorted(list(load_csv("turnos")["id"]))

        # Profesores coincidentes
        cop_df = load_csv("profesores")
        COP = [
            (str(row["uc_1"]), str(row["uc_2"]))
            for _, row in cop_df.iterrows()
            if str(row["uc_1"]) in C and str(row["uc_2"]) in C
        ]  # Only include if both courses exist in C

        # Turnos disponibles por día
        turnos_dia_df = load_csv("turnos_dias")
        Td = {d: [] for d in D}  # Inicializar diccionario vacío para cada día

        # Llenar Td basado en los datos del CSV
        for _, row in turnos_dia_df.iterrows():
            # Intentar diferentes nombres de columnas posibles
            dia = row[turnos_dia_df.columns[0]]  # Primera columna
            turno = row[turnos_dia_df.columns[1]]  # Segunda columna

            if dia in Td:  # Solo agregar si el día está en D
                Td[dia].append(turno)

        # Ordenar los turnos para cada día
        for d in Td:
            Td[d] = sorted(list(set(Td[d])))  # Eliminar duplicados y ordenar

        # Ordenar los turnos para cada día
        for d in Td:
            Td[d].sort()

        # Semestres
        S = list(load_csv("semestres")["id"])

        # Carreras
        K = list(load_csv("carreras")["codigo"])

        # Sugerencias de UCs
        sug_df = load_csv("trayectoria_sugerida")
        SUG = [
            (row["unidad_curricular"], row["semestre"], row["carrera"])
            for _, row in sug_df.iterrows()
            if row["unidad_curricular"] in C  # Solo incluir si la UC existe en C
        ]

        # Pre-asignaciones
        pa_df = load_csv("preasignaciones")
        PA = {}
        for _, row in pa_df.iterrows():
            unidad_curricular = row["unidad_curricular"]
            if unidad_curricular in C:  # Solo incluir si la UC existe en C
                if unidad_curricular not in PA:
                    PA[unidad_curricular] = []
                PA[unidad_curricular].append((row["dia"], row["turno"]))

        # Previaturas
        prev_df = load_csv("previas")
        P = [(str(row["uc"]), str(row["uc_requerida"]))  # Convertir a string
             for _, row in prev_df.iterrows()
             if str(row["uc"]) in C and str(row["uc_requerida"]) in C  # Convertir a string para comparación
             and str(row["uc"]) != str(row["uc_requerida"])]

        # Pares frecuentes
        PARES_UC = list(combinations(C, 2))

        # Unidades curriculares del mismo semestre
        UC_MISMO_SEMESTRE = {
            (c1, c2): True
            for (c1, s1, k1) in SUG
            for (c2, s2, k2) in SUG
            if c1 != c2 and s1 == s2 and k1 == k2
        }

        # ==== PARÁMETROS ====

        # Capacidad por día y turno
        cap_df = load_csv("capacidad")
        cp = {
            (row["id_dia"], row["id_turno"]): row["capacidad"]
            for _, row in cap_df.iterrows()
        }

        # Factor de capacidad
        fac_cp = float(load_csv("datos")["fac_cp"].iloc[0])

        # Inscriptos por UC
        ins_df = load_csv("inscriptos")
        ins = {row["uc"]: row["inscriptos"] for _, row in ins_df.iterrows()}

        # Inscriptos simultáneos
        co_df = load_csv("coincidencia")
        co = {
            (row["uc_1"], row["uc_2"]): row["coincidencia"]
            for _, row in co_df.iterrows()
        }

        # Completar co para todos los pares de UCs
        co.update({(c1, c2): 0 for (c1, c2) in PARES_UC if (c1, c2) not in co})
        co.update({(c2, c1): v for (c1, c2), v in co.items()})
        co.update({(c, c): ins[c] for c in C})

        # Distancia en semestres (pre-calculada)
        def get_dist_sem(c1, c2):
            careers_in_common = [
                k
                for (_, _, k) in SUG
                if any((c1, s1, k) in SUG for s1 in S)
                and any((c2, s2, k) in SUG for s2 in S)
            ]

            if careers_in_common:
                distances = []
                for k in careers_in_common:
                    semester_c1 = [s for c, s, kk in SUG if c == c1 and kk == k][0]
                    semester_c2 = [s for c, s, kk in SUG if c == c2 and kk == k][0]
                    distances.append(abs(semester_c1 - semester_c2))
                return min(distances)
            else:
                return len(S)

        dist_sem = {(c1, c2): get_dist_sem(c1, c2) for c1, c2 in PARES_UC}
        dist_sem.update({(c2, c1): v for (c1, c2), v in dist_sem.items()})

        # Determinar el máximo número de turnos
        max_turns = max(len(Td[d]) for d in D)

        # Crear un diccionario para mapear cada par (día, turno) a un valor de tiempo
        time_value = {}
        for d in D:
            sorted_turns = sorted(Td[d])
            for index, t in enumerate(sorted_turns):
                # Mapear el día a un entero y el turno a una fracción
                time_value[(d, t)] = d + index / (max_turns + 1)

        def get_ds_from_time(time_value):
            differences = set()
            for d1, t1 in time_value:
                for d2, t2 in time_value:
                    differences.add(abs(time_value[(d1, t1)] - time_value[(d2, t2)]))
            return sorted(list(differences))

        DS = get_ds_from_time(time_value)
        M = max(DS)
        dist_peso = {ds: 1 / (ds + 1) for ds in DS}

        # Eliminar cursos sin valores de inscripción
        invalid_courses = [c for c, v in ins.items() if pd.isna(v)]
        if invalid_courses:
            for c in invalid_courses:
                del ins[c]
                if c in C:
                    C.remove(c)

        return {
            # Conjuntos
            "D": D,
            "C": C,
            "T": T,
            "Td": Td,
            "S": S,
            "K": K,
            "SUG": SUG,
            "PA": PA,
            "P": P,
            "COP": COP,
            "PARES_UC": PARES_UC,
            "UC_MISMO_SEMESTRE": UC_MISMO_SEMESTRE,
            "DS": DS,
            # Parámetros
            "cp": cp,
            "fac_cp": fac_cp,
            "ins": ins,
            "co": co,
            "dist_sem": dist_sem,
            "dist_peso": dist_peso,
            "time_value": time_value,
            # Constantes
            "M": M,
        }

    except Exception as e:
        raise Exception(f"Error al cargar los datos desde {dir_name}: {str(e)}")
