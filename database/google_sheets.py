"""
Compatibility/wrapper module expected by the UI (database.google_sheets).
Delegates to services.google_sheets or to the project's root google_sheets.py
(if present). Returns friendly (ok, msg) tuples and never raises on import.
"""
from typing import Tuple, List, Dict, Any, Optional

# Prefer services.google_sheets (our implementation), else fall back to project root google_sheets.py
_mod = None
try:
    from services import google_sheets as svc_gs  # type: ignore
    _mod = svc_gs
except Exception:
    try:
        import google_sheets as root_gs  # type: ignore
        _mod = root_gs
    except Exception:
        _mod = None

from database.csv_handler import cargar_registros
from config.settings import settings


def _resolve_sheet_key(sheet_key: Optional[str] = None) -> Optional[str]:
    """
    Helper function to resolve sheet_key from settings if not provided.
    Returns sheet_key or None.
    """
    if sheet_key:
        return sheet_key
    return settings.get("google_sheets.sheet_key", "") or settings.get("spreadsheet_id", "") or None


def _require_mod():
    if _mod is None:
        return False, "No hay implementación de Google Sheets disponible (services/google_sheets.py ni google_sheets.py)"
    return True, None


def subir_a_google_sheets(registros: List[Dict[str, Any]], sheet_key: str) -> Tuple[bool, str]:
    ok, msg = _require_mod()
    if not ok:
        return False, msg
    try:
        if hasattr(_mod, "subir_a_google_sheets"):
            return _mod.subir_a_google_sheets(registros, sheet_key)
        if hasattr(_mod, "sync_to_google_sheets"):
            return _mod.sync_to_google_sheets(sheet_key)
        return False, "El módulo de Sheets no expone subir_a_google_sheets ni sync_to_google_sheets"
    except Exception as e:
        return False, str(e)


def delete_row_by_id(sheet_key: str, id_value: str) -> Tuple[bool, str]:
    ok, msg = _require_mod()
    if not ok:
        return False, msg
    try:
        if hasattr(_mod, "delete_row_by_id"):
            return _mod.delete_row_by_id(sheet_key, id_value)
        if hasattr(_mod, "sync_in_background"):
            try:
                _mod.sync_in_background({"id": id_value}, operation="delete", sheet_key=sheet_key)
                return True, "Solicitud de eliminación enviada en background"
            except Exception as e:
                return False, f"sync_in_background fallo: {e}"
        return False, "El módulo no implementa delete_row_by_id ni sync_in_background"
    except Exception as e:
        return False, str(e)


def descargar_desde_google_sheets(sheet_key: str) -> Tuple[bool, Any]:
    ok, msg = _require_mod()
    if not ok:
        return False, msg
    try:
        if hasattr(_mod, "descargar_desde_google_sheets"):
            return _mod.descargar_desde_google_sheets(sheet_key)
        # Fallback: try to use get_sheets_service + read range
        if hasattr(_mod, "get_sheets_service"):
            try:
                service, err = _mod.get_sheets_service()
                if err:
                    return False, err
                sheet_name = settings.get("google_sheets.sheet_name", "") or "Sheet1"
                range_name = f"'{sheet_name}'"
                resp = service.spreadsheets().values().get(spreadsheetId=sheet_key, range=range_name).execute()
                values = resp.get("values", []) or []
                if not values:
                    return True, []
                headers = values[0]
                rows = values[1:]
                results = []
                for row in rows:
                    d = {}
                    for i, h in enumerate(headers):
                        key = h if h else f"col{i}"
                        d[key] = row[i] if i < len(row) else ""
                    results.append(d)
                return True, results
            except Exception as e:
                return False, str(e)
        return False, "No hay rutina para descargar la hoja"
    except Exception as e:
        return False, str(e)


# database/google_sheets.py (añadir o asegurar existe)
def sync_from_google_sheets(sheet_key: str) -> Tuple[bool, str]:
    """
    Descarga la hoja y sobrescribe el CSV local (guardar_todos_registros).
    Devuelve (ok,msg).
    """
    try:
        from services.google_sheets import descargar_desde_google_sheets
        ok, result = descargar_desde_google_sheets(sheet_key)
        if not ok:
            return False, result  # mensaje de error

        registros = result or []
        # Alinear keys con CSV_FIELDS: si las keys en la hoja no coinciden, mapear por coincidencia simple
        from database.csv_handler import guardar_todos_registros
        # Si los registros vienen con headers distintos, tratamos de normalizarlos a CSV_FIELDS
        from config.settings import CSV_FIELDS
        if registros:
            # si los headers difieren, reordenamos según CSV_FIELDS para consistencia
            normalized = []
            for r in registros:
                nr = {k: r.get(k, "") for k in CSV_FIELDS}
                # agregar cualquier key extra
                for k in r:
                    if k not in nr:
                        nr[k] = r.get(k, "")
                normalized.append(nr)
        else:
            normalized = []

        ok2, msg2 = guardar_todos_registros(normalized)
        if ok2:
            return True, f"Descargados y guardados {len(normalized)} registros"
        else:
            return False, f"Error guardando CSV: {msg2}"
    except Exception as e:
        import traceback; traceback.print_exc()
        return False, str(e)


def sincronizar_bidireccional(sheet_key: Optional[str] = None) -> Tuple[bool, str]:
    """
    Wrapper para sincronización bidireccional.
    Delega a services.google_sheets.sincronizar_bidireccional si existe.
    """
    ok, msg = _require_mod()
    if not ok:
        return False, msg
    try:
        # Resolver sheet_key usando helper
        sheet_key = _resolve_sheet_key(sheet_key)
        if not sheet_key:
            return False, "No sheet_key configurado"
        
        # Usar la implementación del módulo si existe
        if hasattr(_mod, "sincronizar_bidireccional"):
            return _mod.sincronizar_bidireccional(sheet_key)
        
        # Fallback: hacer sync manual (download + save + upload)
        # 1. Descargar
        ok_down, result = descargar_desde_google_sheets(sheet_key)
        if not ok_down:
            return False, f"Error descargando: {result}"
        
        registros_remotos = result or []
        
        # 2. Guardar localmente
        from database.csv_handler import guardar_todos_registros
        ok_save, msg_save = guardar_todos_registros(registros_remotos)
        if not ok_save:
            return False, f"Error guardando CSV: {msg_save}"
        
        # 3. Subir desde local (para asegurar consistencia)
        registros = cargar_registros()
        ok_up, msg_up = subir_a_google_sheets(registros, sheet_key)
        
        return True, f"Sincronizado: {len(registros)} registros"
    except Exception as e:
        return False, str(e)


def test_google_sheets_connection(sheet_key: Optional[str] = None) -> Tuple[bool, str]:
    ok, msg = _require_mod()
    if not ok:
        return False, msg
    try:
        if hasattr(_mod, "get_sheets_service"):
            service, err = _mod.get_sheets_service()
            if err:
                return False, err
            # Resolve sheet_key using helper
            sheet_key = _resolve_sheet_key(sheet_key)
            if sheet_key:
                try:
                    resp = service.spreadsheets().get(spreadsheetId=sheet_key, fields="properties(title)").execute()
                    title = resp.get("properties", {}).get("title", "<sin título>")
                    return True, f"Conexión OK. Hoja: {title}"
                except Exception as e:
                    return False, f"Conexión falló al acceder al spreadsheet: {e}"
            return True, "Cliente Google Sheets inicializado correctamente (sin sheet_key para verificar hoja)"
        return False, "No hay client helper disponible en el módulo de Sheets"
    except Exception as e:
        return False, str(e)