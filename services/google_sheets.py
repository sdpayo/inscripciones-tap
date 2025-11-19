"""Google Sheets synchronization service."""
import threading
from pathlib import Path
from config.settings import settings, DATA_DIR

# Try to import Google API libraries
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    _HAS_GOOGLE_API = True
except ImportError:
    _HAS_GOOGLE_API = False


def get_google_sheets_service():
    """
    Get Google Sheets service using service account credentials.
    Returns:
        tuple: (service, error_message) - service is None if failed
    """
    if not _HAS_GOOGLE_API:
        return None, "Google API libraries not installed. Install with: pip install google-api-python-client google-auth"
    
    try:
        # Get credentials file path from settings
        creds_file = settings.get("google_sheets.credentials_file", "service_account.json")
        creds_path = Path(creds_file)
        
        # Try different locations
        if not creds_path.exists():
            creds_path = DATA_DIR / creds_file
        
        if not creds_path.exists():
            creds_path = DATA_DIR / "config" / creds_file
        
        if not creds_path.exists():
            return None, f"Service account credentials file not found: {creds_file}"
        
        # Define scopes
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            str(creds_path), scopes=SCOPES
        )
        
        # Build service
        service = build('sheets', 'v4', credentials=credentials)
        
        return service, None
    
    except Exception as e:
        return None, f"Error initializing Google Sheets service: {str(e)}"


def sync_to_google_sheets(registro, operation='insert'):
    """
    Synchronize a single registration to Google Sheets.
    Args:
        registro (dict): Registration data
        operation (str): 'insert' or 'delete'
    Returns:
        tuple: (success, message)
    """
    # Check if sync is enabled
    if not settings.get("google_sheets.enabled", False):
        return True, "Google Sheets sync disabled"
    
    # Get sheet ID from settings
    sheet_id = settings.get("google_sheets.sheet_id", "")
    if not sheet_id:
        return True, "Google Sheets ID not configured"
    
    try:
        # Get service
        service, error = get_google_sheets_service()
        if error:
            # Don't fail if Google Sheets is not configured
            return True, f"Google Sheets not available: {error}"
        
        if operation == 'insert':
            return _sync_insert(service, sheet_id, registro)
        elif operation == 'delete':
            return _sync_delete(service, sheet_id, registro)
        else:
            return False, f"Unknown operation: {operation}"
    
    except Exception as e:
        # Don't fail the main operation if sync fails
        return True, f"Sync error (non-blocking): {str(e)}"


def _sync_insert(service, sheet_id, registro):
    """Insert or update a record in Google Sheets."""
    try:
        from config.settings import CSV_FIELDS
        
        # Get the sheet range
        range_name = settings.get("google_sheets.range", "Sheet1")
        
        # Read existing data to find if record exists
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"{range_name}!A:A"
        ).execute()
        
        values = result.get('values', [])
        
        # Check if headers exist, if not add them
        if not values or len(values) == 0:
            # Add headers
            header_values = [CSV_FIELDS]
            body = {'values': header_values}
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"{range_name}!A1",
                valueInputOption='RAW',
                body=body
            ).execute()
            row_index = 2  # Start after header
        else:
            # Find row with matching ID
            registro_id = registro.get("id", "")
            row_index = None
            
            for idx, row in enumerate(values):
                if row and row[0] == registro_id:
                    row_index = idx + 1
                    break
            
            if row_index is None:
                # Append new row
                row_index = len(values) + 1
        
        # Prepare row data
        row_data = [registro.get(field, "") for field in CSV_FIELDS]
        
        # Update or append
        body = {'values': [row_data]}
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"{range_name}!A{row_index}",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return True, f"Synced to Google Sheets (row {row_index})"
    
    except Exception as e:
        return False, f"Insert sync error: {str(e)}"


def _sync_delete(service, sheet_id, registro):
    """Delete a record from Google Sheets."""
    try:
        range_name = settings.get("google_sheets.range", "Sheet1")
        
        # Read existing data to find row
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"{range_name}!A:A"
        ).execute()
        
        values = result.get('values', [])
        
        # Find row with matching ID
        registro_id = registro.get("id", "")
        row_index = None
        
        for idx, row in enumerate(values):
            if row and row[0] == registro_id:
                row_index = idx
                break
        
        if row_index is None:
            return True, "Record not found in Google Sheets"
        
        # Delete the row
        requests = [{
            'deleteDimension': {
                'range': {
                    'sheetId': 0,  # Assuming first sheet
                    'dimension': 'ROWS',
                    'startIndex': row_index,
                    'endIndex': row_index + 1
                }
            }
        }]
        
        body = {'requests': requests}
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=body
        ).execute()
        
        return True, f"Deleted from Google Sheets (row {row_index + 1})"
    
    except Exception as e:
        return False, f"Delete sync error: {str(e)}"


def sync_in_background(registro, operation='insert'):
    """
    Synchronize in background thread (non-blocking).
    Args:
        registro (dict): Registration data
        operation (str): 'insert' or 'delete'
    """
    def worker():
        try:
            sync_to_google_sheets(registro, operation)
        except Exception:
            # Silent fail in background
            pass
    
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
