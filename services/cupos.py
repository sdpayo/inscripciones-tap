"""
Helpers para cargar cupos por materia y calcular cupos restantes.
Usar desde la UI: from services.cupos import calcular_cupos_restantes, get_cupos
"""
import os, traceback, time
from typing import Tuple, Any, Optional

from config.settings import settings

# Cache de sincronización para evitar sincronizar demasiado frecuentemente
_last_sync_time = None
SYNC_INTERVAL_SECONDS = 300  # 5 minutos

try:
    import yaml
    _HAS_YAML = True
except Exception:
    _HAS_YAML = False

from database.csv_handler import cargar_registros

def _find_cupos_path() -> Optional[str]:
    for key in ("cupos.file", "cupos_file", "cupos.path"):
        val = settings.get(key, None)
        if val:
            if os.path.isabs(val):
                if os.path.exists(val):
                    return val
            else:
                if os.path.exists(val):
                    return val
                try:
                    from config.settings import DATA_DIR
                    p = os.path.join(str(DATA_DIR), val)
                    if os.path.exists(p):
                        return p
                except Exception:
                    pass
    for p in ("data/cupos.yaml", "cupos.yaml", "config/cupos.yaml"):
        if os.path.exists(p):
            return p
    return None

def get_cupos() -> Tuple[bool, Any]:
    try:
        p = _find_cupos_path()
        if not p:
            return False, "No se encontró archivo de cupos (buscado en settings y rutas por defecto)"
        text = open(p, "r", encoding="utf-8").read()
        if _HAS_YAML:
            try:
                data = yaml.safe_load(text)
                return True, (data or {})
            except Exception as e:
                # intentar JSON
                import json
                try:
                    data = json.loads(text)
                    return True, data
                except Exception:
                    return False, f"Error parseando YAML/JSON: {e}"
        else:
            import json
            try:
                data = json.loads(text)
                return True, data
            except Exception:
                return False, "PyYAML no instalado y el archivo no es JSON: instala pyyaml o revisa formato"
    except Exception as e:
        return False, f"Error leyendo cupos: {e}\n{traceback.format_exc()}"

def calcular_cupos_restantes() -> Tuple[bool, Any]:
    """
    Calcula cupos restantes por materia.
    SINCRONIZA DESDE GOOGLE SHEETS SOLO SI PASÓ EL INTERVALO DE CACHE.
    """
    global _last_sync_time
    
    try:
        # 1. SINCRONIZAR DESDE GOOGLE SHEETS SOLO SI PASÓ EL INTERVALO
        now = time.time()
        if _last_sync_time is None or (now - _last_sync_time) > SYNC_INTERVAL_SECONDS:
            sync_attempted = False
            try:
                from database.google_sheets import sincronizar_bidireccional
                from config.settings import settings
                
                if settings.get("google_sheets.enabled", False):
                    sheet_id = (settings.get("google_sheets.spreadsheet_id") or 
                               settings.get("google_sheets.sheet_key") or 
                               settings.get("spreadsheet_id"))
                    
                    if sheet_id:
                        last_sync_msg = f"{int(now - _last_sync_time)}s atrás" if _last_sync_time else "nunca"
                        print(f"[DEBUG] Sincronizando desde Google Sheets (última sync: {last_sync_msg})...")
                        sync_attempted = True
                        ok, msg = sincronizar_bidireccional(sheet_id)
                        if ok:
                            print("[DEBUG] Sincronización exitosa")
                        else:
                            print(f"[WARNING] No se pudo sincronizar: {msg}")
                        # Actualizar timestamp incluso si falló, para evitar reintentos constantes
                        _last_sync_time = now
                    else:
                        print("[DEBUG] Google Sheets habilitado pero no hay sheet_id configurado")
                else:
                    print("[DEBUG] Google Sheets deshabilitado, saltando sincronización")
            except Exception as e:
                print(f"[WARNING] Error en sync previo a contar cupos: {e}")
            
            # Si no se intentó sincronizar (sheets deshabilitado), actualizar timestamp igualmente
            if not sync_attempted:
                _last_sync_time = now
        else:
            elapsed = int(now - _last_sync_time)
            print(f"[DEBUG] Usando cache de sincronización (última sync: {elapsed}s atrás, próxima en {SYNC_INTERVAL_SECONDS - elapsed}s)")
        
        # 2. CARGAR CUPOS CONFIGURADOS
        ok, cupos = get_cupos()
        if not ok:
            cupos = {}
            
        # 3. CONTAR INSCRIPTOS DESDE CSV (YA ACTUALIZADO)
        registros = cargar_registros()
        counts = {}
        for r in registros:
            if str(r.get("en_lista_espera","No")).strip().lower() in ("sí","si","yes","true"):
                continue
            mat = str(r.get("materia","") or "")
            prof = str(r.get("profesor","") or "")
            com = str(r.get("comision","") or "")
            key = (mat, prof, com)
            counts[key] = counts.get(key, 0) + 1
            
        # 4. CALCULAR RESTANTES
        results = {}
        materias_set = set([m for m, p, c in counts.keys()]) | set((list(cupos.keys()) if isinstance(cupos, dict) else []))
        for mat in materias_set:
            cupo_val = None
            if isinstance(cupos, dict) and mat in cupos:
                v = cupos[mat]
                if isinstance(v, dict):
                    cupo_val = v.get("cupo") or v.get("vacantes") or None
                else:
                    try:
                        cupo_val = int(v)
                    except Exception:
                        cupo_val = None
            
            # Contar por profesor y comisión
            profs_comms_for_mat = {}
            for (m, p, c), cnt in counts.items():
                if m == mat:
                    key_pc = (p, c)
                    profs_comms_for_mat[key_pc] = cnt
                    
            if cupo_val is not None:
                total = sum(profs_comms_for_mat.values())
                restante = max(0, cupo_val - total)
                results[mat] = {
                    "cupo": cupo_val,
                    "inscriptos": total,
                    "restante": restante,
                    "profesores_comisiones": profs_comms_for_mat
                }
            else:
                results[mat] = {
                    "cupo": None,
                    "inscriptos": sum(profs_comms_for_mat.values()),
                    "restante": None,
                    "profesores_comisiones": profs_comms_for_mat
                }
                
        return True, results
    except Exception as e:
        return False, f"Error calculando cupos: {e}\n{traceback.format_exc()}"