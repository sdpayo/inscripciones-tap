"""Modelo de materias y profesores."""
import json
from pathlib import Path
from config.settings import INSTRUMENTS_FILE

# Cargar materias desde JSON
MATERIAS = []

def _normalize_from_dict(data_dict):
    """
    Convierte el formato de dict ({"materia": {meta}}) a una lista de registros
    con las claves que maneja la app: materia, profesor, comision, año, cupo, turno, tipo.
    Crea una entrada por cada combinación relevante (años/profesor/comisión).
    """
    items = []
    for materia_name, meta in data_dict.items():
        if not isinstance(meta, dict):
            # formato inesperado: crear un registro mínimo
            items.append({
                "materia": materia_name,
                "profesor": "",
                "comision": "",
                "año": None,
                "cupo": None,
                "turno": "",
                "tipo": ""
            })
            continue

        # Extraer años; permitir int, str o lista
        years = meta.get('years') or meta.get('años') or meta.get('anio') or meta.get('año') or []
        if isinstance(years, (int, str)):
            years = [years]
        # convertir elementos a int cuando sea posible, sino dejar como str
        norm_years = []
        for y in years:
            try:
                norm_years.append(int(y))
            except Exception:
                norm_years.append(y)
        if not norm_years:
            norm_years = [None]  # al menos una iteración

        # profesores
        professors = meta.get('professors') or meta.get('profesores') or {}
        if isinstance(professors, dict):
            prof_list = list(professors.keys()) or [""]
        elif isinstance(professors, list):
            prof_list = professors or [""]
        else:
            prof_list = [""]

        # comisiones
        commissions = meta.get('commissions') or meta.get('commisions') or meta.get('commisiones') or {}
        if isinstance(commissions, dict):
            comm_items = list(commissions.items()) or [(None, None)]
        elif isinstance(commissions, list):
            comm_items = [(c, None) for c in commissions] or [(None, None)]
        else:
            comm_items = [(None, None)]

        tipo = meta.get('type') or meta.get('tipo') or ""
        tipo = tipo.capitalize() if isinstance(tipo, str) else ""

        turno = meta.get('turno') or meta.get('turn') or ""

        # generar entradas: por cada año, por cada profesor y por cada comisión
        for year in norm_years:
            for prof in prof_list:
                # si no hay comisiones definidas (ej. materias grupales), crear una entrada sin comision
                if comm_items and comm_items != [(None, None)]:
                    for com, cap in comm_items:
                        entry = {
                            "materia": materia_name,
                            "profesor": prof or "",
                            "comision": com or "",
                            "año": year,
                            "cupo": cap,
                            "turno": turno,
                            "tipo": tipo
                        }
                        items.append(entry)
                else:
                    # entrada sin comision (grupal u otros)
                    entry = {
                        "materia": materia_name,
                        "profesor": prof or "",
                        "comision": "",
                        "año": year,
                        "cupo": meta.get('cupo') or meta.get('capacity') or None,
                        "turno": turno,
                        "tipo": tipo
                    }
                    items.append(entry)
    return items

def cargar_materias():
    """Carga materias desde instruments.json"""
    global MATERIAS

    if not INSTRUMENTS_FILE.exists():
        print(f"[WARN] No se encontró {INSTRUMENTS_FILE}")
        MATERIAS = []
        return MATERIAS

    try:
        with open(INSTRUMENTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Si es lista, tomar tal cual (pero normalizar 'año' si viene como lista o str)
        if isinstance(data, list):
            # normalize items: ensure 'año' is int when possible
            normalized = []
            for it in data:
                if not isinstance(it, dict):
                    continue
                año = it.get('año') or it.get('anio')
                if isinstance(año, (list, tuple)):
                    # expandir: crear una entrada por cada año en la lista
                    for y in año:
                        new = dict(it)
                        try:
                            new['año'] = int(y)
                        except Exception:
                            new['año'] = y
                        normalized.append(new)
                else:
                    if isinstance(año, str):
                        try:
                            it['año'] = int(año)
                        except Exception:
                            pass
                    normalized.append(it)
            MATERIAS = normalized

        # Si es dict, convertir a lista razonable (y expandir por año)
        elif isinstance(data, dict):
            MATERIAS = _normalize_from_dict(data)

        else:
            MATERIAS = []

        print(f"[INFO] {len(MATERIAS)} materias cargadas (desde {INSTRUMENTS_FILE})")
        return MATERIAS

    except Exception as e:
        print(f"[ERROR] No se pudo cargar materias: {e}")
        MATERIAS = []
        return MATERIAS


# Cargar al importar el módulo
MATERIAS = cargar_materias()


def get_todas_materias():
    """Obtiene lista de todas las materias únicas."""
    materias = set()
    for mat in MATERIAS:
        if "materia" in mat:
            materias.add(mat["materia"])
    return sorted(list(materias))


def get_materias_por_anio(anio):
    """
    Filtra materias por año.
    Ahora soporta que mat['año'] sea int, str o lista.
    """
    materias_set = set()
    for mat in MATERIAS:
        mat_anio = mat.get("año") or mat.get("anio") or mat.get("Año")
        # normalizar
        if isinstance(mat_anio, list):
            if anio in mat_anio:
                materias_set.add(mat.get("materia"))
        else:
            try:
                if mat_anio is not None and int(mat_anio) == int(anio):
                    materias_set.add(mat.get("materia"))
            except Exception:
                # comparación fallback como strings
                if str(mat_anio) == str(anio):
                    materias_set.add(mat.get("materia"))

    result = sorted(list(materias_set))
    print(f"[DEBUG] Año {anio}: {len(result)} materias encontradas")
    return result


def _normalize_anio(mat_anio):
    """Normaliza el campo año para comparaciones: puede ser int, str, list, None."""
    if mat_anio is None:
        return []
    if isinstance(mat_anio, (list, tuple)):
        out = []
        for x in mat_anio:
            try:
                out.append(int(x))
            except Exception:
                try:
                    out.append(int(str(x).strip()))
                except Exception:
                    pass
        return out
    try:
        return [int(mat_anio)]
    except Exception:
        try:
            return [int(str(mat_anio).strip())]
        except Exception:
            return []


def get_profesores_materia(materia, anio=None):
    """
    Devuelve lista de profesores para una materia.
    Si `anio` está dado, intenta filtrar por año.
    Fallback: si no hay resultados exactos, busca por 'instrumento' (texto después de ':')
    y devuelve profesores asociados a ese instrumento (de cualquier año).
    Si aún así no hay profesores, devuelve ['A Designar'] como opción por defecto.
    """
    materia_q = (materia or "").strip()
    profesores = set()

    # 1) Búsqueda exacta materia (+ año si se pasó)
    for mat in MATERIAS:
        if (mat.get("materia") or "").strip() != materia_q:
            continue

        if anio is not None:
            mat_anio_list = _normalize_anio(mat.get("año") or mat.get("anio"))
            if mat_anio_list:
                if int(anio) not in mat_anio_list:
                    continue
            else:
                # si la entrada no tiene año, ignorarla en la búsqueda por año
                continue

        prof = (mat.get("profesor") or "").strip()
        if prof:
            profesores.add(prof)

    # 2) Si encontramos profesores exactos, devolverlos
    if profesores:
        return sorted(profesores)

    # 3) Fallback por "instrumento" (texto después de ':') — buscar substring
    instrument_key = materia_q.lower().split(":", 1)[-1].strip() if ":" in materia_q else materia_q.lower()
    if instrument_key:
        for mat in MATERIAS:
            mat_name = (mat.get("materia") or "").lower()
            if instrument_key not in mat_name:
                continue
            if anio is not None:
                mat_anio_list = _normalize_anio(mat.get("año") or mat.get("anio"))
                # permitir tomar profesores de otros años si no hay lista o si coincide
                if mat_anio_list and int(anio) not in mat_anio_list:
                    # no coincide el año -> aún así podemos aceptar como fallback, así que OMITIMOS esta línea
                    pass
            prof = (mat.get("profesor") or "").strip()
            if prof:
                profesores.add(prof)

    if profesores:
        return sorted(profesores)

    # 4) Ultimate fallback: devolver opción por defecto para que el combo muestre algo
    return ["A Designar"]


def get_comisiones_profesor(materia, profesor, anio=None):
    """
    Devuelve lista de comisiones para materia+profesor (+anio opcional).
    Si no hay comisiones explícitas pero sí existen entradas para el profesor (con comision vacía),
    devuelve [''] para permitir seleccionar al profesor. Si no hay nada, intenta fallback por instrumento.
    """
    materia_q = (materia or "").strip()
    comisiones = set()
    found_prof_entries = False

    # 1) Búsqueda exacta por materia+profesor (+anio si se pasó)
    for mat in MATERIAS:
        if (mat.get("materia") or "").strip() != materia_q:
            continue
        if (profesor or "") != (mat.get("profesor") or ""):
            continue

        if anio is not None:
            mat_anio_list = _normalize_anio(mat.get("año") or mat.get("anio"))
            if mat_anio_list:
                if int(anio) not in mat_anio_list:
                    continue
            else:
                # si no hay año en el registro, continuamos (pero no lo filtramos fuera)
                pass

        found_prof_entries = True
        com = mat.get("comision")
        if com is None:
            com = ""
        comisiones.add(com)

    if found_prof_entries:
        # si solo encontramos comisiones vacías -> devolver ['']
        if not comisiones or (len(comisiones) == 1 and ("" in comisiones)):
            return [""]
        # ordenar con comisiones explícitas primero
        result = sorted(comisiones, key=lambda x: (0 if x else 1, x))
        return result

    # 2) Fallback: buscar por instrumento (texto después de ':') y tomar comisiones para el profesor
    instrument_key = materia_q.lower().split(":", 1)[-1].strip() if ":" in materia_q else materia_q.lower()
    if instrument_key:
        for mat in MATERIAS:
            mat_name = (mat.get("materia") or "").lower()
            if instrument_key not in mat_name:
                continue
            if (profesor or "") != (mat.get("profesor") or ""):
                continue
            # opción: no filtrar por año aquí para tener mayor cobertura
            com = mat.get("comision")
            if com is None:
                com = ""
            comisiones.add(com)

    if comisiones:
        # si solo hay comision vacía devolvemos ['']
        if len(comisiones) == 1 and "" in comisiones:
            return [""]
        return sorted(comisiones, key=lambda x: (0 if x else 1, x))

    # 3) Si no hay nada, devolver lista vacía para que la UI muestre nada o maneje fallback
    return []


def get_horario(materia, profesor, comision):
    """
    Obtiene horario para materia, profesor y comisión.
    Args:
        materia (str): Nombre de la materia
        profesor (str): Nombre del profesor
        comision (str): Comisión
    Returns:
        str: Horario formateado
    """
    for mat in MATERIAS:
        if (mat.get("materia") == materia and
            mat.get("profesor") == profesor and
            mat.get("comision") == comision):

            # Intentar obtener turno
            turno = mat.get("turno") or mat.get("Turno", "")

            if turno:
                return f"Turno: {turno}"

            # Si no hay turno, buscar otros campos de horario
            horario = mat.get("horario") or mat.get("Horario", "")
            if horario:
                return horario

            return "Sin horario definido"

    return ""


def get_info_completa(materia, profesor, comision):
    """
    Obtiene información completa de una materia/profesor/comisión.
    Args:
        materia (str): Nombre de la materia
        profesor (str): Nombre del profesor
        comision (str): Comisión
    Returns:
        dict: Información completa o None
    """
    for mat in MATERIAS:
        if (mat.get("materia") == materia and
            mat.get("profesor") == profesor and
            mat.get("comision") == comision):
            return mat
    return None


def buscar_materias(texto):
    """
    Busca materias que contengan el texto.
    Args:
        texto (str): Texto a buscar
    Returns:
        list: Lista de materias que coinciden
    """
    texto_lower = texto.lower()
    resultados = []

    for mat in MATERIAS:
        materia = mat.get("materia", "")
        if texto_lower in materia.lower():
            resultados.append(materia)

    return sorted(list(set(resultados)))


def get_turnos_disponibles():
    """
    Obtiene lista de turnos únicos disponibles desde el CSV.
    Returns:
        list: Lista de turnos disponibles
    """
    turnos = set()
    for mat in MATERIAS:
        turno = mat.get("turno", "")
        if turno:
            turnos.add(turno)

    # Ordenar para tener consistencia
    return sorted(list(turnos))


def get_estadisticas():
    """
    Obtiene estadísticas de las materias cargadas.
    Returns:
        dict: Estadísticas
    """
    stats = {
        "total_registros": len(MATERIAS),
        "materias_unicas": len(get_todas_materias()),
        "profesores_unicos": len(set(mat.get("profesor","") for mat in MATERIAS)),
        "por_año": {}
    }

    # Contar por año
    for anio in [1, 2, 3, 4]:
        materias_anio = get_materias_por_anio(anio)
        stats["por_año"][anio] = len(materias_anio)

    return stats