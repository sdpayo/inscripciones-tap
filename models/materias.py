"""Modelo de materias y profesores."""
import json
from pathlib import Path
from config.settings import INSTRUMENTS_FILE

# Cargar materias desde JSON
MATERIAS = []

def cargar_materias():
    """Carga materias desde instruments.json"""
    global MATERIAS
    
    if not INSTRUMENTS_FILE.exists():
        print(f"[WARN] No se encontró {INSTRUMENTS_FILE}")
        return []
    
    try:
        with open(INSTRUMENTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            MATERIAS = data if isinstance(data, list) else []
            print(f"[INFO] {len(MATERIAS)} materias cargadas")
            return MATERIAS
    except Exception as e:
        print(f"[ERROR] No se pudo cargar materias: {e}")
        return []


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
    Args:
        anio (int): Año (1, 2, 3, 4)
    Returns:
        list: Lista de materias del año
    """
    materias_set = set()
    for mat in MATERIAS:
        # Intentar diferentes nombres de campo
        mat_anio = mat.get("año") or mat.get("anio") or mat.get("Año")
        if mat_anio == anio:
            materias_set.add(mat["materia"])
    
    result = sorted(list(materias_set))
    print(f"[DEBUG] Año {anio}: {len(result)} materias encontradas")
    return result


def get_profesores_materia(materia):
    """
    Obtiene profesores que dictan una materia.
    Args:
        materia (str): Nombre de la materia
    Returns:
        list: Lista de profesores
    """
    profesores = set()
    for mat in MATERIAS:
        if mat.get("materia") == materia:
            profesores.add(mat["profesor"])
    
    return sorted(list(profesores))


def get_comisiones_profesor(materia, profesor):
    """
    Obtiene comisiones para una materia y profesor.
    Args:
        materia (str): Nombre de la materia
        profesor (str): Nombre del profesor
    Returns:
        list: Lista de comisiones
    """
    comisiones = set()
    for mat in MATERIAS:
        if mat["materia"] == materia and mat["profesor"] == profesor:
            comisiones.add(mat["comision"])
    
    return sorted(list(comisiones))


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
        if (mat["materia"] == materia and 
            mat["profesor"] == profesor and 
            mat["comision"] == comision):
            
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
        if (mat["materia"] == materia and 
            mat["profesor"] == profesor and 
            mat["comision"] == comision):
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


def get_estadisticas():
    """
    Obtiene estadísticas de las materias cargadas.
    Returns:
        dict: Estadísticas
    """
    stats = {
        "total_registros": len(MATERIAS),
        "materias_unicas": len(get_todas_materias()),
        "profesores_unicos": len(set(mat["profesor"] for mat in MATERIAS)),
        "por_año": {}
    }
    
    # Contar por año
    for anio in [1, 2, 3, 4]:
        materias_anio = get_materias_por_anio(anio)
        stats["por_año"][anio] = len(materias_anio)
    
    return stats