import pandas as pd
import os
from itertools import combinations

def cargar_datos_calendario(directorio_datos):
    """
    Carga los conjuntos y parámetros desde archivos CSV para el modelo de calendario
    de evaluaciones.

    Args:
        directorio_datos (str): Ruta al directorio que contiene los archivos CSV

    Returns:
        dict: Diccionario con todos los conjuntos y parámetros del modelo
    """

    def cargar_csv(nombre):
        ruta_archivo = os.path.join(directorio_datos, f"{nombre}.csv")

        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"No se encontró el archivo {ruta_archivo}")

        return pd.read_csv(ruta_archivo)

    try:
        # ==== CONJUNTOS ====

        # Días del calendario
        D = list(cargar_csv("dias")["id"])

        # Unidades curriculares
        C = list(cargar_csv("unidades_curriculares")["codigo"])

        # Turnos
        T = list(cargar_csv("turnos")["id"])

        # Turnos disponibles por día
        turnos_dia_df = cargar_csv("turnos_dias")
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
        S = list(cargar_csv("semestres")["id"])

        # Carreras
        K = list(cargar_csv("carreras")["codigo"])

        # Sugerencias de cursos
        sug_df = cargar_csv("trayectoria_sugerida")
        SUG = [(row["unidad_curricular"], row["semestre"], row["carrera"])
               for _, row in sug_df.iterrows()]

        # Pre-asignaciones
        pa_df = cargar_csv("preasignaciones")
        PA = {}
        for _, row in pa_df.iterrows():
            unidad_curricular = row["unidad_curricular"]
            if unidad_curricular not in PA:
                PA[unidad_curricular] = []
            PA[unidad_curricular].append((row["dia"], row["turno"]))

        # Previaturas
        prev_df = cargar_csv("previas")
        P = [(row["uc"], row["uc_requerida"])
             for _, row in prev_df.iterrows()]

        # Pares frecuentes
        PARES_DIAS = [(d1, d2) for d1 in D for d2 in D]
        PARES_CURSOS = list(combinations(C, 2))

        # Cursos mismo semestre
        cursos_mismo_semestre = {
            (c1, c2): True
            for (c1, s1, k1) in SUG
            for (c2, s2, k2) in SUG
            if c1 != c2 and s1 == s2 and k1 == k2
        }

        # ==== PARÁMETROS ====

        # Capacidad por día y turno
        cap_df = cargar_csv("capacidad")
        cp = {(row["id_dia"], row["id_turno"]): row["capacidad"]
              for _, row in cap_df.iterrows()}

        # Factor de capacidad
        fac_cp = float(cargar_csv("datos")["fac_cp"].iloc[0])

        # Inscriptos por curso
        ins_df = cargar_csv("inscriptos")
        ins = {row["uc"]: row["inscriptos"]
               for _, row in ins_df.iterrows()}

        # Inscriptos simultáneos
        co_df = cargar_csv("coincidencia")
        co = {(row["uc_1"], row["uc_2"]): row["coincidencia"]
              for _, row in co_df.iterrows()}

        # Completar co para todos los pares de cursos
        co.update({(c1, c2): 0 for (c1,c2) in PARES_CURSOS if (c1, c2) not in co})
        co.update({(c2, c1): v for (c1, c2), v in co.items()})
        co.update({(c, c): ins[c] for c in C})

        # Distancia en semestres (pre-calculada)
        def get_dist_sem(c1, c2):
            careers_in_common = [
                k for (_, _, k) in SUG
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

        dist_sem = {(c1, c2): get_dist_sem(c1, c2) for c1, c2 in PARES_CURSOS}
        dist_sem.update({(c2, c1): v for (c1, c2), v in dist_sem.items()})

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
            "PARES_DIAS": PARES_DIAS,
            "PARES_CURSOS": PARES_CURSOS,
            "cursos_mismo_semestre": cursos_mismo_semestre,

            # Parámetros
            "cp": cp,
            "fac_cp": fac_cp,
            "ins": ins,
            "co": co,
            "dist_sem": dist_sem,
        }

    except Exception as e:
        raise Exception(f"Error al cargar los datos desde {directorio_datos}: {str(e)}")
