"""
Handler de CSV con funciones completas y seguras.
Reemplaza/normaliza las operaciones de carga/guardado de inscripciones.
"""
import csv
import tempfile
import shutil
import os
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

from config.settings import CSV_FILE, CSV_FIELDS

# Asegurar que el directorio existe
CSV_FILE.parent.mkdir(parents=True, exist_ok=True)


def cargar_registros() -> List[Dict[str, Any]]:
    """Carga todos los registros desde CSV_FILE. Devuelve lista vacía si no existe."""
    if not CSV_FILE.exists():
        return []

    registros: List[Dict[str, Any]] = []
    try:
        with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalizar keys (en caso de headers inesperados)
                registros.append(dict(row))
    except Exception as e:
        print(f"[ERROR] cargar_registros: no se pudo leer {CSV_FILE}: {e}")
    return registros


def guardar_todos_registros(registros: List[Dict[str, Any]], csv_path: Optional[str] = None,
                            fieldnames: Optional[List[str]] = None) -> Tuple[bool, str]:
    """
    Guarda la lista completa de registros en CSV de forma atómica.
    Devuelve (ok, mensaje).
    """
    try:
        if csv_path is None:
            csv_path = str(CSV_FILE.resolve())

        if fieldnames is None:
            # Preferir CSV_FIELDS del settings; si faltan usar keys del primer registro
            fieldnames = CSV_FIELDS.copy() if CSV_FIELDS else []
            if not fieldnames and registros:
                fieldnames = list(registros[0].keys())

        # Asegurar directorio
        dirn = os.path.dirname(csv_path) or "."
        os.makedirs(dirn, exist_ok=True)

        # Escribir a archivo temporal y moverlo (atomic-ish)
        fd, tmp_path = tempfile.mkstemp(prefix="tmp_inscripciones_", dir=dirn, text=True)
        os.close(fd)
        try:
            with open(tmp_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                for r in registros:
                    # asegurarnos de que todos los valores sean strings (csv writer espera)
                    row = {k: ("" if r.get(k) is None else r.get(k)) for k in fieldnames}
                    writer.writerow(row)
            shutil.move(tmp_path, csv_path)
        finally:
            # cleanup si queda tmp
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
        return True, "OK"
    except Exception as e:
        tb = traceback.format_exc()
        print("[ERROR] guardar_todos_registros failed:", e)
        print(tb)
        return False, str(e)


def guardar_registro(registro: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Guarda o actualiza un registro individual.
    - Si 'id' no existe se genera con generar_id(registro)
    - Devuelve (ok,msg)
    """
    try:
        registros = cargar_registros()

        # Generar id si no existe
        if not registro.get("id"):
            registro["id"] = generar_id(registro)

        # Añadir fecha_inscripcion si no existe
        if not registro.get("fecha_inscripcion"):
            registro["fecha_inscripcion"] = datetime.now().isoformat()

        # Buscar por id y reemplazar si existe
        encontrado = False
        for i, r in enumerate(registros):
            if str(r.get("id", "")) == str(registro.get("id", "")):
                registros[i] = registro
                encontrado = True
                break
        if not encontrado:
            registros.append(registro)

        ok, msg = guardar_todos_registros(registros)
        return ok, msg
    except Exception as e:
        return False, f"Error al guardar registro: {e}"


def generar_id(registro: Optional[Dict[str, Any]] = None) -> str:
    """
    Genera un ID legible y (relativamente) único:
    formato: {LEGAJO|DNI|TEMP}_{YYYYMMDD}_{HHMMSS}_{rand}
    """
    base = "TEMP"
    if registro:
        base = registro.get("legajo") or registro.get("dni") or base
    base = "".join(c for c in str(base) if c.isalnum()) or "TEMP"
    now = datetime.now()
    ts = now.strftime("%Y%m%d_%H%M%S")
    # añadir componente corto aleatorio para reducir colisiones
    import random, string
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{base}_{ts}_{rand}"


def actualizar_registro(datos: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Actualiza un registro existente por 'id'. Lanza ValueError si no existe id.
    Devuelve (ok,msg).
    """
    try:
        registros = cargar_registros()
        reg_id = datos.get("id")
        if not reg_id:
            return False, "El registro debe incluir 'id' para actualizar"

        encontrado = False
        for i, r in enumerate(registros):
            if str(r.get("id", "")) == str(reg_id):
                # Mantener columnas según CSV_FIELDS (si existen)
                actualizado = {k: datos.get(k, r.get(k, "")) for k in (CSV_FIELDS or list(datos.keys()))}
                registros[i] = actualizado
                encontrado = True
                break

        if not encontrado:
            return False, f"Registro con id '{reg_id}' no encontrado"

        ok, msg = guardar_todos_registros(registros)
        return ok, msg
    except Exception as e:
        return False, str(e)


def eliminar_registro(reg_id: str) -> Tuple[bool, str]:
    """
    Elimina un registro por ID. Devuelve (ok,msg).
    """
    try:
        registros = cargar_registros()
        registros_filtrados = [r for r in registros if str(r.get("id", "")) != str(reg_id)]
        if len(registros_filtrados) == len(registros):
            return False, f"Registro con id '{reg_id}' no encontrado"
        ok, msg = guardar_todos_registros(registros_filtrados)
        return ok, msg
    except Exception as e:
        return False, str(e)


def buscar_por_dni(dni: str) -> List[Dict[str, Any]]:
    registros = cargar_registros()
    return [r for r in registros if str(r.get("dni", "")) == str(dni)]


def buscar_por_id(reg_id: str) -> Optional[Dict[str, Any]]:
    registros = cargar_registros()
    for r in registros:
        if str(r.get("id", "")) == str(reg_id):
            return r
    return None


def sync_before_count():
    """Sincroniza desde Google Sheets antes de contar inscripciones."""
    try:
        from database.google_sheets import sincronizar_bidireccional
        from config.settings import settings
        
        if not settings.get("google_sheets.enabled", False):
            return False, "Google Sheets deshabilitado"
            
        sheet_id = (settings.get("google_sheets.spreadsheet_id") or 
                   settings.get("google_sheets.sheet_key") or 
                   settings.get("spreadsheet_id"))
        
        if not sheet_id:
            return False, "No hay sheet_id configurado"
            
        return sincronizar_bidireccional(sheet_id)
    except Exception as e:
        return False, f"Error: {e}"


def contar_inscripciones_materia(materia: str, profesor: Optional[str] = None,
                                 comision: Optional[str] = None, 
                                 excluir_lista_espera: bool = True,
                                 force_sync: bool = True) -> int:
    """
    Cuenta inscripciones filtrando por materia, opcionalmente por profesor y comisión.
    
    Args:
        materia: nombre de la materia (requerido)
        profesor: nombre del profesor (opcional)
        comision: nombre/código de la comisión (opcional)
        excluir_lista_espera: si True, no cuenta registros en lista de espera
        force_sync: si True, sincroniza desde Sheets antes de contar
    
    Returns:
        int: cantidad de inscripciones que cumplen los filtros
    """
    # Sincronizar antes de contar si force_sync=True
    if force_sync:
        try:
            sync_before_count()
        except Exception as e:
            print(f"[WARNING] No se pudo sincronizar antes de contar: {e}")
    
    registros = cargar_registros()
    count = 0
    
    for r in registros:
        # Excluir lista de espera si corresponde
        if excluir_lista_espera:
            en_espera = str(r.get("en_lista_espera", "No")).strip().lower()
            if en_espera in ("sí", "si", "yes", "true", "1"):
                continue
        
        # Filtrar por materia (requerido)
        mat = str(r.get("materia", "") or "").strip()
        if mat != materia:
            continue
        
        # Filtrar por profesor si se especifica
        if profesor:
            prof = str(r.get("profesor", "") or "").strip()
            if prof != profesor:
                continue
        
        # Filtrar por comisión si se especifica
        if comision:
            com = str(r.get("comision", "") or "").strip()
            if com != comision:
                continue
        
        count += 1
    
    return count


def obtener_historial_alumno(dni: str) -> List[Dict[str, Any]]:
    registros = cargar_registros()
    historial = [r for r in registros if str(r.get("dni", "")) == str(dni)]
    historial.sort(key=lambda x: x.get("fecha_inscripcion", ""), reverse=True)
    return historial


def exportar_listado(filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    registros = cargar_registros()
    if not filtros:
        return registros
    resultado = []
    for r in registros:
        cumple = True
        if "materia" in filtros and r.get("materia") != filtros["materia"]:
            cumple = False
        if "profesor" in filtros and r.get("profesor") != filtros["profesor"]:
            cumple = False
        if "turno" in filtros and r.get("turno") != filtros["turno"]:
            cumple = False
        if "anio" in filtros and str(r.get("anio")) != str(filtros["anio"]):
            cumple = False
        if cumple:
            resultado.append(r)
    return resultado


def migrar_id_si_es_uuid(registro: Dict[str, Any]) -> Dict[str, Any]:
    id_actual = registro.get("id", "")
    if len(id_actual) > 20 and id_actual.count("-") >= 4:
        nuevo_id = generar_id(registro)
        registro["id"] = nuevo_id
        print(f"[INFO] ID migrado: {id_actual[:8]}... -> {nuevo_id}")
    return registro