# Funciones clave para sincronización con Google Sheets (services/google_sheets.py)
import threading, os, traceback
from typing import List, Dict, Any, Tuple, Optional
from config.settings import settings

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    _HAS_GOOGLE = True
except Exception:
    _HAS_GOOGLE = False

def verify_remote_sync(sheet_id: str, sheet_name: Optional[str] = None) -> Tuple[bool, Any]:
    """
    Descarga la hoja indicada e imprime conteo y primeras filas.
    Úsalo para verificar qué hay realmente en Google Sheets después de un push.
    Retorna (ok, values|mensaje).
    """
    try:
        service, err = get_sheets_service()
        if err:
            print("[VERIFY] No se puede inicializar client:", err)
            return False, err

        # Resolver nombre de hoja
        sheet_name = sheet_name or settings.get("google_sheets.sheet_name", "") or None

        # Obtener metadata para elegir la primera hoja si no se indicó sheet_name
        ss_meta = service.spreadsheets().get(spreadsheetId=sheet_id, fields="sheets.properties").execute()
        sheets_meta = ss_meta.get("sheets", []) or []
        if not sheet_name:
            if not sheets_meta:
                msg = "Spreadsheet no contiene hojas"
                print("[VERIFY]", msg)
                return False, msg
            sheet_name = sheets_meta[0].get("properties", {}).get("title", "Sheet1")

        # Construir rango y leer
        range_name = f"'{sheet_name}'"
        resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = resp.get("values", []) or []

        print("[VERIFY] sheet_id:", sheet_id, "sheet_name:", sheet_name)
        print("[VERIFY] filas leídas (incl header):", len(values))
        print("[VERIFY] sample (primeras filas):")
        for i, row in enumerate(values[:8]):
            print(f"  {i+1}: {row}")

        return True, values
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, str(e)
    
def get_sheets_service(credentials_file: Optional[str] = None) -> Tuple[Optional[Any], Optional[str]]:
    """
    Crea y devuelve el servicio de Google Sheets.
    Retorna (service, error_msg). Si service is None, error_msg explica por qué.
    """
    if not _HAS_GOOGLE:
        return None, "google-api-python-client o google-auth no están instalados"

    try:
        creds_path = credentials_file or settings.get("google_sheets.credentials_file", "") or settings.get("google_sheets.credentials_file", "")
        if creds_path and not os.path.isabs(creds_path):
            candidate = os.path.abspath(creds_path)
            if os.path.exists(candidate):
                creds_path = candidate
            else:
                try:
                    from config.settings import DATA_DIR
                    candidate2 = str(DATA_DIR / creds_path)
                    if os.path.exists(candidate2):
                        creds_path = candidate2
                except Exception:
                    pass

        if creds_path and os.path.exists(creds_path):
            creds = service_account.Credentials.from_service_account_file(creds_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        else:
            try:
                from google.auth import default
                creds, _ = default(scopes=["https://www.googleapis.com/auth/spreadsheets"])
            except Exception as e_adc:
                return None, f"No se encontraron credenciales (service account file {creds_path} no existe y ADC falló): {e_adc}"

        service = build("sheets", "v4", credentials=creds, cache_discovery=False)
        return service, None
    except Exception as e:
        return None, f"Error inicializando cliente Google Sheets: {e}"

def delete_row_by_id(sheet_id: str, id_value: str, sheet_name: Optional[str] = None) -> Tuple[bool, str]:
    """
    Busca filas que contengan id_value en la primera columna y las elimina.
    Devuelve (ok, mensaje).
    """
    if not _HAS_GOOGLE:
        return False, "google libraries not available"
    try:
        service, err = get_sheets_service()
        if err:
            return False, err
        sheet_name = sheet_name or settings.get("google_sheets.sheet_name", "") or "Sheet1"
        range_all = f"'{sheet_name}'!A:A"
        resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_all).execute()
        values = resp.get("values", []) or []
        matched_indices = []
        for idx, row in enumerate(values):
            cell = row[0] if row else ""
            if str(cell).strip() == str(id_value).strip():
                matched_indices.append(idx)  # 0-based
        if not matched_indices:
            return True, "No se encontraron filas con ese ID"
        ss = service.spreadsheets().get(spreadsheetId=sheet_id, fields="sheets.properties").execute()
        sheets = ss.get("sheets", []) or []
        target_sheet_id = None
        for s in sheets:
            props = s.get("properties", {})
            if props.get("title") == sheet_name or target_sheet_id is None:
                target_sheet_id = props.get("sheetId")
        if target_sheet_id is None:
            return False, "No se pudo determinar sheetId"
        matched_rows = sorted(set(matched_indices), reverse=True)
        requests = []
        for r in matched_rows:
            requests.append({
                "deleteDimension": {
                    "range": {
                        "sheetId": target_sheet_id,
                        "dimension": "ROWS",
                        "startIndex": int(r),
                        "endIndex": int(r + 1)
                    }
                }
            })
        body = {"requests": requests}
        service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body=body).execute()
        return True, f"Deleted {len(requests)} rows"
    except HttpError as he:
        return False, f"Google API error: {he}"
    except Exception as e:
        tb = traceback.format_exc()
        print("[ERROR] delete_row_by_id:", e)
        print(tb)
        return False, str(e)

def subir_a_google_sheets(registros: List[Dict[str, Any]], sheet_id: str, sheet_name: Optional[str] = None,
                          header_order: Optional[List[str]] = None) -> Tuple[bool, str]:
    """
    Reemplaza contenido de la hoja con 'registros'. DEBUG VERBOSE:
    - imprime headers y primeras filas que se enviarán
    - después de write hace una lectura inmediata para verificar lo que quedó
    """
    if not _HAS_GOOGLE:
        return False, "google libraries not available"

    try:
        service, err = get_sheets_service()
        if err:
            return False, err

        # obtener metadata
        ss_meta = service.spreadsheets().get(spreadsheetId=sheet_id, fields="sheets.properties").execute()
        sheets_meta = ss_meta.get("sheets", []) or []
        sheet_titles = [s.get("properties", {}).get("title", "") for s in sheets_meta]

        # determinar sheet_name
        sheet_name = sheet_name or settings.get("google_sheets.sheet_name", "") or (sheet_titles[0] if sheet_titles else "Sheet1")
        if sheet_name not in sheet_titles:
            # intentar crear hoja si no existe (ya intentado en implementaciones anteriores)
            try:
                service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={"requests":[{"addSheet":{"properties":{"title":sheet_name}}}] }).execute()
                # refrescar
                ss_meta = service.spreadsheets().get(spreadsheetId=sheet_id, fields="sheets.properties").execute()
                sheets_meta = ss_meta.get("sheets", []) or []
                sheet_titles = [s.get("properties", {}).get("title", "") for s in sheets_meta]
            except Exception as e_add:
                # no fatal, seguir con lo que haya
                print(f"[WARN] subir_a_google_sheets: no se pudo crear '{sheet_name}': {e_add}")

        # determinar headers
        if header_order:
            headers = header_order
        else:
            if registros:
                try:
                    from config.settings import CSV_FIELDS
                    headers = [h for h in CSV_FIELDS if h in registros[0].keys()] or list(registros[0].keys())
                except Exception:
                    headers = list(registros[0].keys())
            else:
                try:
                    from config.settings import CSV_FIELDS
                    headers = CSV_FIELDS.copy()
                except Exception:
                    headers = []

        # construir valores que enviaremos
        values = [headers]
        for r in registros:
            row = [r.get(k, "") for k in headers]
            values.append(row)

        # LOG: mostrar info que vamos a enviar (no sensible: solo keys/longitud y primeras filas)
        print("[DEBUG] subir_a_google_sheets: sheet_id=", sheet_id, "sheet_name=", sheet_name)
        print("[DEBUG] subir_a_google_sheets: headers count=", len(headers), "headers=", headers)
        print("[DEBUG] subir_a_google_sheets: filas a escribir (incl header)=", len(values))
        sample_rows = values[1:6]  # primeras 5 filas de datos
        print("[DEBUG] subir_a_google_sheets: sample rows:", sample_rows)

        # preparar rango seguro para escritura
        import re
        needs_quote = bool(re.search(r"[^\w]", sheet_name))
        if needs_quote:
            safe_sheet_name = sheet_name.replace("'", "''")
            name_for_range = f"'{safe_sheet_name}'"
        else:
            name_for_range = sheet_name
        clear_range = f"{name_for_range}!A1:ZZ"
        write_range_base = f"{name_for_range}!A1"

        # intentar clear (capturar errores)
        try:
            service.spreadsheets().values().clear(spreadsheetId=sheet_id, range=clear_range).execute()
        except Exception as e_clear:
            print(f"[WARN] subir_a_google_sheets: clear failed for range {clear_range}: {e_clear}")

        # hacer update
        try:
            body = {"values": values}
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=write_range_base,
                valueInputOption="RAW",
                body=body
            ).execute()
        except Exception as e_upd:
            print("[ERROR] subir_a_google_sheets: update fail:", e_upd)
            return False, str(e_upd)

        # READBACK: leer inmediatamente lo escrito y comparar
        try:
            read_range = f"{name_for_range}"
            resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=read_range).execute()
            read_values = resp.get("values", []) or []
            print("[DEBUG] subir_a_google_sheets: readback filas leídas (incl header)=", len(read_values))
            # mostrar primeras filas leídas
            print("[DEBUG] subir_a_google_sheets: readback sample:", read_values[:6])
        except Exception as e_rb:
            print("[WARN] subir_a_google_sheets: readback failed:", e_rb)

        return True, f"Wrote {len(values)-1} rows to '{sheet_name}'"
    except Exception as e:
        import traceback; traceback.print_exc()
        return False, str(e)
    
def sync_to_google_sheets(sheet_id: str) -> Tuple[bool, str]:
    """Push completo: sube todos los registros locales a la hoja sheet_id."""
    try:
        from database.csv_handler import cargar_registros
        regs = cargar_registros()
        return subir_a_google_sheets(regs, sheet_id)
    except Exception as e:
        return False, str(e)

def sync_incremental_to_sheets(sheet_id: str, hours_window: int = 24) -> Tuple[bool, Dict[str, Any]]:
    """
    Sincronización incremental inteligente hacia Google Sheets.
    Solo procesa cambios recientes (últimas N horas).
    
    Args:
        sheet_id: ID del spreadsheet
        hours_window: Ventana de tiempo en horas para considerar cambios (default 24h)
    
    Returns:
        (ok, stats_dict) con contadores de added/updated/deleted
    """
    print(f"[SYNC_INCREMENTAL] Iniciando sincronización incremental (ventana: {hours_window}h)")
    
    try:
        from datetime import datetime, timedelta
        from database.csv_handler import cargar_registros
        
        # 1. Cargar registros locales
        local_records = cargar_registros()
        print(f"[SYNC_INCREMENTAL] Cargados {len(local_records)} registros locales")
        
        # 2. Descargar registros remotos
        ok, result = descargar_desde_google_sheets(sheet_id)
        if not ok:
            return False, {"error": f"Error descargando desde Sheets: {result}"}
        remote_records = result or []
        print(f"[SYNC_INCREMENTAL] Descargados {len(remote_records)} registros remotos")
        
        # 3. Indexar por ID
        local_by_id = {str(r.get("id", "")): r for r in local_records if r.get("id")}
        remote_by_id = {str(r.get("id", "")): r for r in remote_records if r.get("id")}
        
        # 4. Calcular fecha límite (solo registros de las últimas N horas)
        now = datetime.now()
        cutoff = now - timedelta(hours=hours_window)
        print(f"[SYNC_INCREMENTAL] Fecha límite: {cutoff.isoformat()}")
        
        # 5. Encontrar cambios
        local_ids = set(local_by_id.keys())
        remote_ids = set(remote_by_id.keys())
        
        # Nuevos registros (existen local pero no remoto)
        new_ids = local_ids - remote_ids
        
        # Registros eliminados (existen remoto pero no local)
        deleted_ids = remote_ids - local_ids
        
        # Registros potencialmente modificados (existen en ambos)
        common_ids = local_ids & remote_ids
        
        # Filtrar por ventana de tiempo solo para nuevos/modificados
        recent_new_ids = set()
        for rid in new_ids:
            rec = local_by_id[rid]
            fecha_str = str(rec.get("fecha_inscripcion", ""))
            if fecha_str:
                try:
                    fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
                    if fecha >= cutoff:
                        recent_new_ids.add(rid)
                except Exception:
                    # Si no se puede parsear fecha, incluir de todas formas
                    recent_new_ids.add(rid)
            else:
                # Sin fecha, incluir
                recent_new_ids.add(rid)
        
        print(f"[SYNC_INCREMENTAL] Registros nuevos totales: {len(new_ids)}, recientes: {len(recent_new_ids)}")
        print(f"[SYNC_INCREMENTAL] Registros eliminados: {len(deleted_ids)}")
        
        # 6. Aplicar cambios incrementales
        stats = {"added": 0, "updated": 0, "deleted": 0, "unchanged": len(common_ids)}
        
        if not recent_new_ids and not deleted_ids:
            print("[SYNC_INCREMENTAL] No hay cambios que sincronizar")
            return True, stats
        
        # Construir nueva lista remota
        new_remote = []
        
        # Mantener registros remotos existentes que no fueron eliminados
        for rid in remote_ids:
            if rid not in deleted_ids:
                new_remote.append(remote_by_id[rid])
        
        # Agregar nuevos registros recientes
        for rid in recent_new_ids:
            new_remote.append(local_by_id[rid])
            stats["added"] += 1
        
        stats["deleted"] = len(deleted_ids)
        
        print(f"[SYNC_INCREMENTAL] Total registros a enviar a Sheets: {len(new_remote)}")
        
        # 7. Subir a Sheets
        ok, msg = subir_a_google_sheets(new_remote, sheet_id)
        if not ok:
            return False, {"error": msg}
        
        print(f"[SYNC_INCREMENTAL] ✓ Sincronización completada: {stats}")
        return True, stats
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, {"error": str(e)}

def descargar_desde_google_sheets(sheet_id: str, sheet_name: Optional[str] = None) -> Tuple[bool, Any]:
    """Descarga hoja remota y devuelve (True, list_of_dicts) o (False, mensaje)."""
    if not _HAS_GOOGLE:
        return False, "google libraries not available"
    try:
        print(f"[DOWNLOAD] Iniciando descarga desde sheet_id: {sheet_id[:20]}...")
        service, err = get_sheets_service()
        if err:
            print(f"[DOWNLOAD] Error obteniendo servicio: {err}")
            return False, err
        sheet_name = sheet_name or settings.get("google_sheets.sheet_name", "") or None
        print(f"[DOWNLOAD] Obteniendo metadata de la hoja...")
        ss_meta = service.spreadsheets().get(spreadsheetId=sheet_id, fields="sheets.properties").execute()
        sheets = ss_meta.get("sheets", []) or []
        if not sheets:
            print("[DOWNLOAD] No se encontraron hojas en el spreadsheet")
            return True, []
        if not sheet_name:
            sheet_name = sheets[0].get("properties", {}).get("title", "Sheet1")
        print(f"[DOWNLOAD] Usando sheet_name: {sheet_name}")
        range_name = f"'{sheet_name}'"
        print(f"[DOWNLOAD] Descargando rango: {range_name}")
        resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = resp.get("values", []) or []
        print(f"[DOWNLOAD] Total filas descargadas (incluyendo header si existe): {len(values)}")
        if not values:
            print("[DOWNLOAD] La hoja está vacía")
            return True, []
        
        # Verificar si la primera fila es header o son datos
        has_header_row = settings.get("google_sheets.has_header_row", False)
        print(f"[DOWNLOAD] Configuración has_header_row: {has_header_row}")
        
        if has_header_row:
            # La primera fila son headers
            headers = [h.strip() if isinstance(h, str) else str(h) for h in values[0]]
            rows = values[1:]
            print(f"[DOWNLOAD] Usando headers de la primera fila: {headers[:10]}..." if len(headers) > 10 else f"[DOWNLOAD] Headers: {headers}")
        else:
            # NO hay header, usar CSV_FIELDS
            try:
                from config.settings import CSV_FIELDS
                headers = CSV_FIELDS.copy() if CSV_FIELDS else []
            except Exception:
                headers = []
            
            if not headers:
                print("[DOWNLOAD] ERROR: No hay CSV_FIELDS definido y la hoja no tiene headers")
                return False, "No se pueden mapear los datos sin headers"
            
            rows = values  # Todas las filas son datos
            print(f"[DOWNLOAD] NO hay header en Sheets, usando CSV_FIELDS: {headers[:10]}..." if len(headers) > 10 else f"[DOWNLOAD] CSV_FIELDS: {headers}")
        
        print(f"[DOWNLOAD] Filas de datos (sin header): {len(rows)}")
        if rows:
            print(f"[DOWNLOAD] Muestra fila 1: {rows[0][:5] if len(rows[0]) > 5 else rows[0]}")
            if len(rows) > 1:
                print(f"[DOWNLOAD] Muestra fila 2: {rows[1][:5] if len(rows[1]) > 5 else rows[1]}")
        
        results = []
        for row_idx, row in enumerate(rows):
            d = {}
            for i, h in enumerate(headers):
                d[h] = row[i] if i < len(row) else ""
            results.append(d)
            
            # Log de muestra para los primeros registros
            if row_idx < 2:
                print(f"[DOWNLOAD] Registro {row_idx+1} mapeado: nombre={d.get('nombre', 'N/A')}, apellido={d.get('apellido', 'N/A')}, dni={d.get('dni', 'N/A')}, materia={d.get('materia', 'N/A')}")
        
        print(f"[DOWNLOAD] Total registros procesados: {len(results)}")
        
        # GUARDAR RESPALDO LOCAL AUTOMÁTICO
        try:
            from config.settings import DATA_DIR
            from database.csv_handler import guardar_todos_registros
            from datetime import datetime
            
            backup_file = DATA_DIR / "inscripciones_sheets.csv"
            print(f"[DOWNLOAD] Guardando respaldo local en {backup_file}...")
            ok_backup, msg_backup = guardar_todos_registros(results, csv_path=str(backup_file))
            if ok_backup:
                print(f"[DOWNLOAD] ✓ Respaldo local guardado exitosamente ({len(results)} registros)")
                
                # Guardar timestamp del último respaldo
                timestamp_file = DATA_DIR / "inscripciones_sheets_timestamp.txt"
                with open(timestamp_file, 'w', encoding='utf-8') as f:
                    f.write(datetime.now().isoformat())
            else:
                print(f"[DOWNLOAD] ⚠ Error guardando respaldo: {msg_backup}")
        except Exception as e_backup:
            print(f"[DOWNLOAD] ⚠ Error creando respaldo local: {e_backup}")
            # No es crítico, continuar
        
        return True, results
    except Exception as e:
        import traceback; traceback.print_exc()
        return False, str(e)

def sync_in_background(registro: Dict[str, Any], operation: str = "insert", sheet_key: Optional[str] = None, use_incremental: bool = True) -> Tuple[bool, str]:
    """
    Ejecuta la operación en background (no bloqueante).
    
    Args:
        registro: Registro a procesar
        operation: Tipo de operación ('insert', 'update', 'delete')
        sheet_key: ID del spreadsheet (opcional, usa settings si no se provee)
        use_incremental: Si True, usa sync incremental (más eficiente)
    """
    def worker():
        try:
            sk = sheet_key or settings.get("google_sheets.sheet_key", "") or settings.get("google_sheets.spreadsheet_id", "")
            if not sk:
                print("[INFO] sync_in_background: no sheet_key configurado")
                return
            
            if operation == "delete":
                print(f"[SYNC_BG] Procesando eliminación de registro {registro.get('id', 'N/A')}")
                # Para delete, usar sync incremental que maneja la eliminación
                if use_incremental:
                    ok, result = sync_incremental_to_sheets(sk, hours_window=72)  # 3 días de ventana
                    if isinstance(result, dict):
                        print(f"[SYNC_BG] Delete incremental: {result}")
                    else:
                        print(f"[SYNC_BG] Delete result: {result}")
                else:
                    # Fallback: push completo
                    ok, msg = sync_to_google_sheets(sk)
                    print("[INFO] sync_in_background post-delete push:", ok, msg)
                return
            
            # insert/update
            if use_incremental:
                print(f"[SYNC_BG] Procesando {operation} incremental")
                ok, result = sync_incremental_to_sheets(sk, hours_window=24)
                if isinstance(result, dict):
                    print(f"[SYNC_BG] {operation} incremental: {result}")
                else:
                    print(f"[SYNC_BG] {operation} result: {result}")
            else:
                # Fallback: push completo
                ok, msg = sync_to_google_sheets(sk)
                print("[INFO] sync_in_background push all:", ok, msg)
                
        except Exception as e:
            print("[ERROR] sync_in_background worker exception:", e)
            import traceback
            traceback.print_exc()

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return True, "Worker started"

def load_local_backup() -> Tuple[bool, Any]:
    """
    Carga el respaldo local de Google Sheets (inscripciones_sheets.csv).
    Útil cuando no hay conexión o falla la sincronización.
    
    Returns:
        (ok, registros_or_error)
    """
    try:
        from config.settings import DATA_DIR
        backup_file = DATA_DIR / "inscripciones_sheets.csv"
        timestamp_file = DATA_DIR / "inscripciones_sheets_timestamp.txt"
        
        if not backup_file.exists():
            return False, "No existe respaldo local de Google Sheets"
        
        print(f"[BACKUP] Cargando respaldo local desde {backup_file}...")
        
        # Leer timestamp
        last_sync = "desconocida"
        if timestamp_file.exists():
            try:
                with open(timestamp_file, 'r', encoding='utf-8') as f:
                    last_sync = f.read().strip()
                    from datetime import datetime
                    dt = datetime.fromisoformat(last_sync)
                    last_sync = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
        
        # Cargar registros
        import csv
        registros = []
        with open(backup_file, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                registros.append(dict(row))
        
        print(f"[BACKUP] ✓ Cargados {len(registros)} registros del respaldo (última sync: {last_sync})")
        return True, registros
        
    except Exception as e:
        print(f"[BACKUP] Error cargando respaldo local: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

def smart_sync_to_sheets(sheet_id: str, force_full: bool = False) -> Tuple[bool, Any]:
    """
    Sincronización inteligente que elige automáticamente el mejor método.
    
    Args:
        sheet_id: ID del spreadsheet
        force_full: Si True, fuerza sincronización completa
    
    Returns:
        (ok, result) - result puede ser stats dict o mensaje string
    """
    try:
        # Leer configuración
        sync_mode = settings.get("google_sheets.sync_mode", "incremental")
        sync_window = settings.get("google_sheets.sync_window_hours", 24)
        
        if force_full or sync_mode == "full":
            print("[SMART_SYNC] Usando sincronización COMPLETA")
            from database.csv_handler import cargar_registros
            registros = cargar_registros()
            ok, msg = subir_a_google_sheets(registros, sheet_id)
            return ok, {"mode": "full", "message": msg} if ok else (False, msg)
        else:
            print(f"[SMART_SYNC] Usando sincronización INCREMENTAL (ventana: {sync_window}h)")
            return sync_incremental_to_sheets(sheet_id, hours_window=sync_window)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, str(e)

def sincronizar_bidireccional(sheet_id: str, sheet_name: Optional[str] = None) -> Tuple[bool, str]:
    """
    Sincronización bidireccional con Google Sheets.
    1. Descarga TODOS los registros desde Google Sheets (rango abierto)
    2. Guarda en CSV local
    3. Sube cambios locales a Google Sheets
    Devuelve (ok, mensaje).
    """
    try:
        print("[DEBUG] sincronizar_bidireccional: Sincronizando desde Google Sheets...")
        
        # 1. Descargar desde Sheets con rango abierto
        ok, data = descargar_desde_google_sheets(sheet_id, sheet_name)
        if not ok:
            return False, f"Error descargando desde Sheets: {data}"
        
        registros_remotos = data or []
        print(f"[DEBUG] sincronizar_bidireccional: Descargados {len(registros_remotos)} registros")
        
        # 2. Guardar en CSV local
        from database.csv_handler import guardar_todos_registros, cargar_registros
        ok_save, msg_save = guardar_todos_registros(registros_remotos)
        if not ok_save:
            return False, f"Error guardando CSV local: {msg_save}"
        
        # 3. Subir cambios locales (si los hay) - push completo para asegurar consistencia
        registros_locales = cargar_registros()
        ok_upload, msg_upload = subir_a_google_sheets(registros_locales, sheet_id, sheet_name)
        if not ok_upload:
            print(f"[WARN] sincronizar_bidireccional: Error subiendo a Sheets: {msg_upload}")
            # No es crítico, ya tenemos los datos locales actualizados
        
        return True, f"Sincronizado correctamente: {len(registros_locales)} registros"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, str(e)

# Reemplaza la función sync_remote_to_local en services/google_sheets.py por esta versión
def sync_remote_to_local(sheet_key: Optional[str] = None, sheet_name: Optional[str] = None, replace_local: bool = True) -> Tuple[bool, Any]:
    """
    Descarga la hoja remota y sincroniza el CSV local.
    - sheet_key: spreadsheet id. Si None toma settings.
    - sheet_name: nombre de la hoja (opcional).
    - replace_local: si True, el CSV local será reemplazado por el contenido remoto (mirror).
    Retorna (True, stats) donde stats es dict {'added':n,'updated':n,'removed':n,'skipped':n}
    o (False, mensaje_error).
    Esta versión importa localmente las funciones necesarias y hace fallback seguro para generar IDs.
    """
    print("[SYNC] ========== INICIANDO SYNC_REMOTE_TO_LOCAL ==========")
    try:
        # imports locales para evitar NameError si no están en top-level
        try:
            from database.csv_handler import cargar_registros, guardar_todos_registros
        except Exception as e_imp:
            print("[WARN] sync_remote_to_local: no se pudieron importar helpers CSV:", e_imp)
            return False, f"No se encontraron helpers CSV: {e_imp}"

        # resolver sheet_key desde settings si no fue provisto
        sk = sheet_key or settings.get("google_sheets.sheet_key", "") or settings.get("spreadsheet_id", "")
        if not sk:
            print("[SYNC] Error: No sheet_key configurado")
            return False, "No sheet_key configurado"
        
        print(f"[SYNC] sheet_key: {sk[:20]}... (truncado)")

        print("[SYNC] Descargando datos desde Google Sheets...")
        ok, result = descargar_desde_google_sheets(sk)  # uses sheet_name from settings if needed
        if not ok:
            print(f"[SYNC] Error descargando desde Sheets: {result}")
            return False, f"Error descargando hoja: {result}"

        remote_records = result or []
        print(f"[SYNC] Descargados {len(remote_records)} registros desde Google Sheets")
        if remote_records:
            print(f"[SYNC] Muestra primer registro remoto keys: {list(remote_records[0].keys())[:10]}")
            print(f"[SYNC] Muestra primer registro remoto values: {list(remote_records[0].values())[:10]}")
            # Verificar si los registros tienen datos reales más allá del ID
            non_empty_fields = [k for k, v in remote_records[0].items() if v and str(v).strip()]
            print(f"[SYNC] Campos no vacíos en primer registro: {non_empty_fields}")
        
        # cargar registros locales
        try:
            print("[SYNC] Cargando registros locales...")
            local_records = cargar_registros()
            print(f"[SYNC] Cargados {len(local_records)} registros locales")
        except Exception as e_lr:
            print("[WARN] sync_remote_to_local: no se pudo cargar registros locales:", e_lr)
            local_records = []

        # Obtener campos de referencia (CSV_FIELDS preferidos)
        try:
            from config.settings import CSV_FIELDS
            csv_fields = CSV_FIELDS.copy() if CSV_FIELDS else []
        except Exception:
            csv_fields = []

        # Build index by id
        local_by_id = {}
        for r in local_records:
            rid = str(r.get("id", "") or "")
            if rid:
                local_by_id[rid] = r

        # Preparar función para generar id si falta
        try:
            # intentar importar la función generar_id si existe en el proyecto
            from utils import generar_id as _gen_id  # intenta nombre común
        except Exception:
            try:
                from helpers import generar_id as _gen_id
            except Exception:
                _gen_id = None

        # fallback a uuid si no hay generar_id
        import uuid

        remote_by_id = {}
        skipped = 0
        records_without_id = 0
        empty_records = 0
        
        for idx, r in enumerate(remote_records):
            # Verificar si el registro está completamente vacío (solo tiene valores vacíos)
            non_empty_values = [v for k, v in r.items() if k != 'id' and v and str(v).strip()]
            if not non_empty_values:
                empty_records += 1
                print(f"[SYNC] Registro {idx+1} está completamente vacío, saltando...")
                skipped += 1
                continue
            
            rid = str(r.get("id", "") or "").strip()
            if not rid:
                records_without_id += 1
                print(f"[SYNC] Registro {idx+1} sin ID, generando uno...")
                print(f"[SYNC]   Datos: nombre={r.get('nombre', 'N/A')}, apellido={r.get('apellido', 'N/A')}, dni={r.get('dni', 'N/A')}")
                
                # attempt to create sensible id from legajo/dni using generar_id if available
                if _gen_id:
                    try:
                        new_id = _gen_id(r)
                        rid = str(new_id or "")
                        r["id"] = rid
                        print(f"[SYNC]   ID generado con generar_id: {rid[:20]}...")
                    except Exception as e_gen:
                        print(f"[SYNC]   Error usando generar_id: {e_gen}")
                        rid = ""
                else:
                    # fallback: uuid based on dni/legajo if present else random
                    try:
                        base = (str(r.get("dni") or "") + "_" + str(r.get("legajo") or "")).strip("_")
                        if base:
                            # determinísticamente derive uuid5 from base + materia to avoid collisions
                            rid = str(uuid.uuid5(uuid.NAMESPACE_URL, base + str(r.get("materia", "") or "")))
                            print(f"[SYNC]   ID generado con UUID5 desde dni/legajo: {rid[:20]}...")
                        else:
                            rid = str(uuid.uuid4())
                            print(f"[SYNC]   ID generado con UUID4 aleatorio: {rid[:20]}...")
                        r["id"] = rid
                    except Exception as e_uuid:
                        print(f"[SYNC]   Error generando UUID: {e_uuid}")
                        rid = ""
            if not rid:
                print(f"[SYNC] Registro {idx+1} no pudo obtener ID, saltando...")
                skipped += 1
                continue
            remote_by_id[rid] = r

        print(f"[SYNC] Procesados {len(remote_by_id)} registros remotos con ID")
        print(f"[SYNC] Registros sin ID inicial: {records_without_id}")
        print(f"[SYNC] Registros completamente vacíos: {empty_records}")
        print(f"[SYNC] Total skipped: {skipped}")
        if remote_by_id:
            first_remote_id = list(remote_by_id.keys())[0]
            first_remote_rec = remote_by_id[first_remote_id]
            print(f"[SYNC] Primer registro en remote_by_id:")
            print(f"[SYNC]   ID: {first_remote_id}")
            print(f"[SYNC]   Keys: {list(first_remote_rec.keys())[:10]}")
            print(f"[SYNC]   Sample values: nombre={first_remote_rec.get('nombre', 'N/A')}, apellido={first_remote_rec.get('apellido', 'N/A')}, dni={first_remote_rec.get('dni', 'N/A')}")

        local_ids = set(local_by_id.keys())
        remote_ids = set(remote_by_id.keys())

        added_ids = remote_ids - local_ids
        removed_ids = local_ids - remote_ids if replace_local else set()
        common_ids = local_ids & remote_ids

        updated_count = 0
        for cid in common_ids:
            local_r = local_by_id.get(cid, {})
            remote_r = remote_by_id.get(cid, {})
            # compare relevant fields
            keys_to_check = csv_fields if csv_fields else list(set(list(local_r.keys()) + list(remote_r.keys())))
            changed = False
            for k in keys_to_check:
                lv = "" if local_r.get(k) is None else str(local_r.get(k))
                rv = "" if remote_r.get(k) is None else str(remote_r.get(k))
                if lv != rv:
                    changed = True
                    break
            if changed:
                updated_count += 1

        # build new local list (mirror or merge)
        new_local = []
        if csv_fields:
            ordered_keys = csv_fields
        else:
            if remote_records:
                ordered_keys = list(remote_records[0].keys())
            elif local_records:
                ordered_keys = list(local_records[0].keys())
            else:
                ordered_keys = ["id"]

        if replace_local:
            # Use stable ordering based on remote_records insertion order
            # remote_by_id is not ordered by original order, so iterate remote_records to preserve order
            for rec in remote_records:
                rid = str(rec.get("id", "") or "")
                if not rid:
                    continue
                # ensure we include all ordered_keys (fill missing with "")
                nr = {k: ("" if rec.get(k) is None else rec.get(k)) for k in ordered_keys}
                for k in rec:
                    if k not in nr:
                        nr[k] = rec.get(k, "")
                new_local.append(nr)
            print(f"[SYNC] Construido new_local con {len(new_local)} registros (modo replace)")
            if new_local:
                print(f"[SYNC] Primer registro de new_local: nombre={new_local[0].get('nombre', 'N/A')}, apellido={new_local[0].get('apellido', 'N/A')}, dni={new_local[0].get('dni', 'N/A')}")
        else:
            local_map = {r.get("id"): r for r in local_records if r.get("id")}
            for rid, lrec in local_map.items():
                if rid in remote_by_id:
                    rec = remote_by_id[rid]
                    merged = {k: ("" if rec.get(k) is None else rec.get(k)) for k in ordered_keys}
                    for k in rec:
                        if k not in merged:
                            merged[k] = rec.get(k, "")
                    new_local.append(merged)
                else:
                    new_local.append(lrec)
            for rid in added_ids:
                rec = remote_by_id[rid]
                nr = {k: ("" if rec.get(k) is None else rec.get(k)) for k in ordered_keys}
                for k in rec:
                    if k not in nr:
                        nr[k] = rec.get(k, "")
                new_local.append(nr)

        # Save atomically
        print(f"[SYNC] Preparando guardar {len(new_local)} registros en CSV local...")
        print(f"[SYNC] Campos a guardar: {ordered_keys[:10]}..." if len(ordered_keys) > 10 else f"[SYNC] Campos: {ordered_keys}")
        if new_local:
            print(f"[SYNC] Muestra del primer registro: {list(new_local[0].keys())[:5]}")
        
        ok_save, msg_save = guardar_todos_registros(new_local)
        if not ok_save:
            print(f"[ERROR] sync_remote_to_local: Error guardando CSV: {msg_save}")
            return False, f"Error guardando CSV local: {msg_save}"
        
        print(f"[SYNC] CSV guardado exitosamente con {len(new_local)} registros")

        stats = {
            "added": len(added_ids),
            "updated": updated_count,
            "removed": len(removed_ids),
            "skipped": skipped,
            "local_total_after": len(new_local)
        }
        print("[INFO] sync_remote_to_local stats:", stats)
        return True, stats
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, str(e)