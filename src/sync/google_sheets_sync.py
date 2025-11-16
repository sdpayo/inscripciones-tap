"""Google Sheets synchronization functionality."""
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Optional
from pathlib import Path
from ..models import Student
from ..config import Config


class GoogleSheetsSync:
    """Synchronize data with Google Sheets."""
    
    def __init__(self, credentials_file: str = None, sheet_id: str = None):
        """
        Initialize Google Sheets sync.
        
        Args:
            credentials_file: Path to Google service account credentials JSON
            sheet_id: Google Sheets ID
        """
        self.credentials_file = credentials_file or Config.GOOGLE_CREDENTIALS_FILE
        self.sheet_id = sheet_id or Config.GOOGLE_SHEET_ID
        self.client = None
        self.spreadsheet = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Sheets API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Check if credentials file exists
            creds_path = Path(self.credentials_file)
            if not creds_path.exists():
                print(f"Credentials file not found: {self.credentials_file}")
                print("Please download your service account credentials from Google Cloud Console")
                return False
            
            # Define the scope
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Authenticate
            creds = Credentials.from_service_account_file(self.credentials_file, scopes=scope)
            self.client = gspread.authorize(creds)
            
            # Open spreadsheet
            if self.sheet_id:
                self.spreadsheet = self.client.open_by_key(self.sheet_id)
            
            return True
        
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def create_spreadsheet(self, title: str = None) -> Optional[str]:
        """
        Create a new spreadsheet.
        
        Args:
            title: Spreadsheet title
        
        Returns:
            Spreadsheet ID if created successfully, None otherwise
        """
        try:
            if not self.client:
                if not self.authenticate():
                    return None
            
            if not title:
                title = f"{Config.PROGRAM_NAME} - Inscripciones"
            
            spreadsheet = self.client.create(title)
            self.spreadsheet = spreadsheet
            self.sheet_id = spreadsheet.id
            
            return spreadsheet.id
        
        except Exception as e:
            print(f"Error creating spreadsheet: {e}")
            return None
    
    def sync_students(self, students: List[Student], worksheet_name: str = "Inscriptos") -> bool:
        """
        Sync students to Google Sheets.
        
        Args:
            students: List of students to sync
            worksheet_name: Name of the worksheet
        
        Returns:
            True if sync successful, False otherwise
        """
        try:
            if not self.client:
                if not self.authenticate():
                    return False
            
            if not self.spreadsheet:
                print("No spreadsheet selected. Please set sheet_id or create a new spreadsheet.")
                return False
            
            # Get or create worksheet
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
                worksheet.clear()
            except gspread.exceptions.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)
            
            # Prepare header
            headers = [
                'ID', 'Nombre', 'Apellido', 'DNI', 'Fecha Nacimiento',
                'Email', 'Teléfono', 'Dirección', 'Ciudad', 'Provincia',
                'Código Postal', 'Contacto Emergencia', 'Tel. Emergencia',
                'Relación', 'Instrumento', 'Nivel', 'Experiencia Previa',
                'Fecha Inscripción', 'Estado', 'Notas'
            ]
            
            # Prepare data
            data = [headers]
            for student in students:
                row = [
                    student.id or '',
                    student.nombre,
                    student.apellido,
                    student.dni,
                    student.fecha_nacimiento,
                    student.email,
                    student.telefono,
                    student.direccion,
                    student.ciudad,
                    student.provincia,
                    student.codigo_postal or '',
                    student.contacto_emergencia_nombre or '',
                    student.contacto_emergencia_telefono or '',
                    student.contacto_emergencia_relacion or '',
                    student.instrumento or '',
                    student.nivel or '',
                    student.experiencia_previa or '',
                    student.fecha_inscripcion,
                    student.estado,
                    student.notas or ''
                ]
                data.append(row)
            
            # Update worksheet
            worksheet.update('A1', data)
            
            # Format header row
            worksheet.format('A1:T1', {
                'backgroundColor': {'red': 0.1, 'green': 0.14, 'blue': 0.49},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                'horizontalAlignment': 'CENTER'
            })
            
            # Freeze header row
            worksheet.freeze(rows=1)
            
            return True
        
        except Exception as e:
            print(f"Error syncing students: {e}")
            return False
    
    def get_students_from_sheet(self, worksheet_name: str = "Inscriptos") -> List[Student]:
        """
        Get students from Google Sheets.
        
        Args:
            worksheet_name: Name of the worksheet
        
        Returns:
            List of students
        """
        try:
            if not self.client:
                if not self.authenticate():
                    return []
            
            if not self.spreadsheet:
                print("No spreadsheet selected. Please set sheet_id.")
                return []
            
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            records = worksheet.get_all_records()
            
            students = []
            for record in records:
                try:
                    student = Student(
                        id=record.get('ID') or None,
                        nombre=record['Nombre'],
                        apellido=record['Apellido'],
                        dni=record['DNI'],
                        fecha_nacimiento=record['Fecha Nacimiento'],
                        email=record['Email'],
                        telefono=record['Teléfono'],
                        direccion=record['Dirección'],
                        ciudad=record.get('Ciudad', 'Salta'),
                        provincia=record.get('Provincia', 'Salta'),
                        codigo_postal=record.get('Código Postal', ''),
                        contacto_emergencia_nombre=record.get('Contacto Emergencia', ''),
                        contacto_emergencia_telefono=record.get('Tel. Emergencia', ''),
                        contacto_emergencia_relacion=record.get('Relación', ''),
                        instrumento=record.get('Instrumento', ''),
                        nivel=record.get('Nivel', ''),
                        experiencia_previa=record.get('Experiencia Previa', ''),
                        fecha_inscripcion=record.get('Fecha Inscripción', ''),
                        estado=record.get('Estado', 'Pendiente'),
                        notas=record.get('Notas', '')
                    )
                    students.append(student)
                except Exception as e:
                    print(f"Error parsing student record: {e}")
            
            return students
        
        except Exception as e:
            print(f"Error getting students from sheet: {e}")
            return []
    
    def share_spreadsheet(self, email: str, role: str = 'reader') -> bool:
        """
        Share spreadsheet with an email address.
        
        Args:
            email: Email address to share with
            role: Permission role ('reader', 'writer', 'owner')
        
        Returns:
            True if shared successfully, False otherwise
        """
        try:
            if not self.spreadsheet:
                print("No spreadsheet selected.")
                return False
            
            self.spreadsheet.share(email, perm_type='user', role=role)
            return True
        
        except Exception as e:
            print(f"Error sharing spreadsheet: {e}")
            return False
