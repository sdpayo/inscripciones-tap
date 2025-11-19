"""Handler de CSV con funciones completas."""
import csv
from pathlib import Path
from datetime import datetime
from config.settings import CSV_FILE, CSV_FIELDS  # ← Corregido
from typing import List, Dict, Optional
import uuid


def guardar_registro(registro: Dict) -> tuple:
    """
    Guarda un registro en el CSV.
    Args:
        registro (dict): Datos del registro
    Returns:
        tuple(bool, str): (exito, mensaje)
    """
    try:
        # Generar ID si no existe
        if not registro.get("id"):
            registro["id"] = generar_id()
        
        # Agregar timestamp si no existe
        if not registro.get("fecha_inscripcion"):
            registro["fecha_inscripcion"] = datetime.now().isoformat()
        
        # Cargar registros existentes
        registros = cargar_registros()
        
        # Verificar si ya existe (por ID)
        existe = False
        for i, reg in enumerate(registros):
            if reg.get("id") == registro["id"]:
                registros[i] = registro
                existe = True
                break
        
        if not existe:
            registros.append(registro)
        
        # Guardar todos los registros
        return guardar_todos_registros(registros)
    
    except Exception as e:
        return False, f"Error al guardar: {e}"
    

def cargar_registros() -> List[Dict]:
    """Carga todos los registros desde CSV."""
    if not CSV_FILE.exists():  # ← Corregido
        return []
    
    registros = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8-sig', newline='') as f:  # ← Corregido
            reader = csv.DictReader(f)
            for row in reader:
                registros.append(dict(row))
    except Exception as e:
        print(f"[ERROR] No se pudo cargar CSV: {e}")
    
    return registros


def guardar_todos_registros(registros: List[Dict]) -> tuple:
    """
    Guarda todos los registros en el CSV.
    Args:
        registros (list): Lista de registros
    Returns:
        tuple(bool, str): (exito, mensaje)
    """
    try:
        # Asegurar que existe el directorio
        CSV_FILE.parent.mkdir(parents=True, exist_ok=True)  # ← Corregido
        
        with open(CSV_FILE, 'w', encoding='utf-8-sig', newline='') as f:  # ← Corregido
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            
            for reg in registros:
                # Asegurar que tiene todos los campos
                row = {field: reg.get(field, "") for field in CSV_FIELDS}
                writer.writerow(row)
        
        return True, f"Guardados {len(registros)} registros"
    
    except Exception as e:
        return False, f"Error al guardar: {e}"


def generar_id(registro=None):
    """
    Genera ID único basado en legajo + fecha + hora.
    Formato: {LEGAJO}_{YYYYMMDD}_{HHMMSS}
    
    Args:
        registro (dict, optional): Datos del registro (debe tener 'legajo' o 'dni')
    
    Returns:
        str: ID único
    """
    # Obtener legajo (o DNI como fallback)
    legajo = ""
    if registro:
        legajo = registro.get("legajo", "") or registro.get("dni", "")
    
    if not legajo:
        # Si no hay legajo ni DNI, generar temporal con timestamp
        legajo = "TEMP"
    
    # Limpiar legajo (solo alfanuméricos)
    legajo = "".join(c for c in str(legajo) if c.isalnum())
    
    # Generar timestamp
    now = datetime.now()
    fecha = now.strftime("%Y%m%d")  # YYYYMMDD
    hora = now.strftime("%H%M%S")   # HHMMSS (con segundos)
    
    # Formato: LEGAJO_FECHA_HORA
    id_generado = f"{legajo}_{fecha}_{hora}"
    
    return id_generado


def actualizar_registro(datos):
    """
    Actualiza un registro existente.
    Args:
        datos (dict): Datos del registro (debe incluir 'id')
    """
    registros = cargar_registros()
    reg_id = datos.get("id")
    
    if not reg_id:
        raise ValueError("El registro debe tener 'id' para actualizar")
    
    # Buscar y actualizar
    encontrado = False
    for i, reg in enumerate(registros):
        if reg.get("id") == reg_id:
            # Mantener todos los campos
            registro_actualizado = {campo: datos.get(campo, reg.get(campo, "")) for campo in CSV_FIELDS}
            registros[i] = registro_actualizado
            encontrado = True
            break
    
    if not encontrado:
        raise ValueError(f"Registro con id '{reg_id}' no encontrado")
    
    guardar_todos_registros(registros)


def eliminar_registro(reg_id):
    """
    Elimina un registro por ID.
    Args:
        reg_id (str): ID del registro a eliminar
    """
    registros = cargar_registros()
    
    # Filtrar (mantener todos menos el eliminado)
    registros_filtrados = [reg for reg in registros if reg.get("id") != reg_id]
    
    if len(registros_filtrados) == len(registros):
        raise ValueError(f"Registro con id '{reg_id}' no encontrado")
    
    guardar_todos_registros(registros_filtrados)


def buscar_por_dni(dni):
    """
    Busca registros por DNI.
    Args:
        dni (str): DNI a buscar
    Returns: list[dict]
    """
    registros = cargar_registros()
    return [reg for reg in registros if reg.get("dni") == dni]


def buscar_por_id(reg_id):
    """
    Busca un registro por ID.
    Args:
        reg_id (str): ID del registro
    Returns: dict or None
    """
    registros = cargar_registros()
    for reg in registros:
        if reg.get("id") == reg_id:
            return reg
    return None


def contar_inscripciones_materia(materia, profesor=None, comision=None):
    """
    Cuenta inscripciones en una materia/profesor/comisión.
    Args:
        materia (str): Nombre de la materia
        profesor (str, optional): Nombre del profesor
        comision (str, optional): Nombre de la comisión
    Returns: int
    """
    registros = cargar_registros()
    
    count = 0
    for reg in registros:
        if reg.get("materia") != materia:
            continue
        
        if profesor and reg.get("profesor") != profesor:
            continue
        
        if comision and reg.get("comision") != comision:
            continue
        
        # No contar los que están en lista de espera
        if reg.get("en_lista_espera", "No") == "Sí":
            continue
        
        count += 1
    
    return count


def obtener_historial_alumno(dni):
    """
    Obtiene historial completo de un alumno por DNI.
    Args:
        dni (str): DNI del alumno
    Returns: list[dict]
    """
    registros = cargar_registros()
    historial = [reg for reg in registros if reg.get("dni") == dni]
    
    # Ordenar por fecha de inscripción (más reciente primero)
    historial.sort(
        key=lambda x: x.get("fecha_inscripcion", ""),
        reverse=True
    )
    
    return historial


def exportar_listado(filtros=None):
    """
    Exporta listado filtrado.
    Args:
        filtros (dict, optional): Filtros a aplicar (materia, profesor, turno, año)
    Returns: list[dict]
    """
    registros = cargar_registros()
    
    if not filtros:
        return registros
    
    resultado = []
    for reg in registros:
        cumple = True
        
        if "materia" in filtros and reg.get("materia") != filtros["materia"]:
            cumple = False
        
        if "profesor" in filtros and reg.get("profesor") != filtros["profesor"]:
            cumple = False
        
        if "turno" in filtros and reg.get("turno") != filtros["turno"]:
            cumple = False
        
        if "anio" in filtros and str(reg.get("anio")) != str(filtros["anio"]):
            cumple = False
        
        if cumple:
            resultado.append(reg)
    
    return resultado


def migrar_id_si_es_uuid(registro):
    """
    Migra IDs antiguos UUID a nuevo formato.
    Args:
        registro (dict): Registro a verificar y migrar si es necesario
    Returns:
        dict: Registro con ID actualizado si fue necesario
    """
    id_actual = registro.get("id", "")
    
    # Si es UUID (formato: 12663a87-6791-deb2-7789-...)
    # Los UUIDs tienen múltiples guiones y son largos (>20 caracteres)
    if len(id_actual) > 20 and id_actual.count("-") >= 4:
        # Regenerar ID
        nuevo_id = generar_id(registro)
        registro["id"] = nuevo_id
        print(f"[INFO] ID migrado: {id_actual[:8]}... -> {nuevo_id}")
    
    return registro