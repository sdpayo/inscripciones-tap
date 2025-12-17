"""
Helpers para cargar cupos por materia y calcular cupos restantes.
Usar desde la UI: from services.cupos import calcular_cupos_restantes, get_cupos
"""
import os, traceback
from typing import Tuple, Any, Optional

from config.settings import settings

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
    SINCRONIZA DESDE GOOGLE SHEETS PRIMERO.
    """
    try:
        # 1. SINCRONIZAR DESDE GOOGLE SHEETS PRIMERO
        try:
            from database.google_sheets import sync_from_google_sheets
            from config.settings import settings
            
            if settings.get("google_sheets.enabled", False):
                sheet_id = settings.get("google_sheets.spreadsheet_id")
                
                if sheet_id:
                    print("[DEBUG] Sincronizando desde Google Sheets antes de contar cupos...")
                    ok, msg = sync_from_google_sheets(sheet_id)
                    if ok:
                        print("[DEBUG] Sincronización exitosa")
                    else:
                        print(f"[WARNING] No se pudo sincronizar: {msg}")
        except Exception as e:
            print(f"[WARNING] Error en sync previo a contar cupos: {e}")
        
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
            com = str(r.get("comision","") or "")
            key = (mat, com)
            counts[key] = counts.get(key, 0) + 1
            
        # 4. CALCULAR RESTANTES
        results = {}
        materias_set = set([m for m,_ in counts.keys()]) | set((list(cupos.keys()) if isinstance(cupos, dict) else []))
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
            
            # Contar por comisión
            comms_for_mat = {}
            for (m, c), cnt in counts.items():
                if m == mat:
                    comms_for_mat[c] = cnt
                    
            if cupo_val is not None:
                total = sum(comms_for_mat.values())
                restante = max(0, cupo_val - total)
                results[mat] = {
                    "cupo": cupo_val,
                    "inscriptos": total,
                    "restante": restante,
                    "comisiones": comms_for_mat
                }
            else:
                results[mat] = {
                    "cupo": None,
                    "inscriptos": sum(comms_for_mat.values()),
                    "restante": None,
                    "comisiones": comms_for_mat
                }
                
        return True, results
    except Exception as e:
        return False, f"Error calculando cupos: {e}\n{traceback.format_exc()}"