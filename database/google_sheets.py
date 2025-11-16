"""Integración con Google Sheets."""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from pathlib import Path
from config.settings import settings, DATA_DIR

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TOKEN_FILE = DATA_DIR / 'token.pickle'


def _get_credentials():
    """Obtiene credenciales de Google."""
    creds = None
    
    # Cargar token guardado
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Buscar credentials.json
            creds_file = settings.get("google_sheets.credentials_file", "credentials.json")
            creds_path = Path(creds_file)
            
            if not creds_path.exists():
                creds_path = DATA_DIR / creds_file
            
            if not creds_path.exists():
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar credenciales
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds


def test_google_sheets_connection(sheet_key):
    """
    Prueba conexión con Google Sheets.
    Args:
        sheet_key (str): ID de la hoja
    Returns:
        tuple(bool, str): (exito, mensaje)
    """
    try:
        credentials = _get_credentials()
        if not credentials:
            return False, "No hay credenciales. Descargá credentials.json desde Google Cloud Console."
        
        service = build('sheets', 'v4', credentials=credentials)
        
        # Intentar leer metadata de la hoja
        sheet = service.spreadsheets().get(spreadsheetId=sheet_key).execute()
        title = sheet.get('properties', {}).get('title', 'Sin título')
        
        return True, f"✅ Conectado a: {title}"
    
    except FileNotFoundError:
        return False, "No se encontró credentials.json"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"


def descargar_desde_google_sheets(sheet_key):
    """
    Descarga datos desde Google Sheets.
    Args:
        sheet_key (str): ID de la hoja
    Returns:
        tuple(bool, list): (exito, registros o mensaje de error)
    """
    try:
        credentials = _get_credentials()
        if not credentials:
            return False, "No hay credenciales configuradas"
        
        service = build('sheets', 'v4', credentials=credentials)
        
        # Leer datos (asumiendo que están en la primera hoja)
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_key,
            range='A:Z'  # Todas las columnas
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            return False, "La hoja está vacía"
        
        # Primera fila = headers
        headers = values[0]
        registros = []
        
        for row in values[1:]:
            # Asegurar que la fila tenga suficientes columnas
            while len(row) < len(headers):
                row.append("")
            
            registro = dict(zip(headers, row))
            registros.append(registro)
        
        return True, registros
    
    except Exception as e:
        return False, f"Error al descargar: {e}"


def subir_a_google_sheets(registros, sheet_key):
    """
    Sube registros a Google Sheets.
    Args:
        registros (list): Lista de registros
        sheet_key (str): ID de la hoja
    Returns:
        tuple(bool, str): (exito, mensaje)
    """
    try:
        credentials = _get_credentials()
        if not credentials:
            return False, "No hay credenciales configuradas"
        
        service = build('sheets', 'v4', credentials=credentials)
        
        # Convertir registros a formato de filas
        from config.settings import CSV_FIELDS
        
        # Headers
        values = [CSV_FIELDS]
        
        # Datos
        for reg in registros:
            row = [reg.get(field, "") for field in CSV_FIELDS]
            values.append(row)
        
        # Limpiar hoja primero
        service.spreadsheets().values().clear(
            spreadsheetId=sheet_key,
            range='A:Z'
        ).execute()
        
        # Subir datos
        body = {'values': values}
        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_key,
            range='A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return True, f"Subidos {len(registros)} registros a Google Sheets"
    
    except Exception as e:
        return False, f"Error al subir a Google Sheets: {e}"


def sincronizar_bidireccional(sheet_key):
    """
    Sincronización bidireccional: merge local + remoto.
    Args:
        sheet_key (str): ID de la hoja
    Returns:
        tuple(bool, str): (exito, mensaje)
    """
    from database.csv_handler import cargar_registros, guardar_todos_registros
    
    try:
        # Cargar datos locales
        locales = cargar_registros()
        locales_dict = {r.get("id"): r for r in locales}
        
        # Descargar datos remotos
        ok, remotos = descargar_desde_google_sheets(sheet_key)
        if not ok:
            return False, remotos
        
        remotos_dict = {r.get("id"): r for r in remotos}
        
        # Merge: combinar ambos
        merged = {}
        
        # Agregar todos los locales
        for id_reg, reg in locales_dict.items():
            merged[id_reg] = reg
        
        # Agregar remotos nuevos o más recientes
        for id_reg, reg_remoto in remotos_dict.items():
            if id_reg not in merged:
                merged[id_reg] = reg_remoto
            else:
                # Comparar fechas de modificación si existen
                fecha_local = merged[id_reg].get("fecha_inscripcion", "")
                fecha_remota = reg_remoto.get("fecha_inscripcion", "")
                
                if fecha_remota > fecha_local:
                    merged[id_reg] = reg_remoto
        
        # Guardar localmente
        registros_finales = list(merged.values())
        guardar_todos_registros(registros_finales)
        
        # Subir a Google Sheets
        ok_subir, msg_subir = subir_a_google_sheets(registros_finales, sheet_key)
        
        return True, f"Sincronización completa: {len(registros_finales)} registros"
    
    except Exception as e:
        return False, f"Error en sincronización: {e}"