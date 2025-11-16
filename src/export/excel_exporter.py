"""Excel export functionality."""
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List
from ..models import Student
from ..config import Config


class ExcelExporter:
    """Export data to Excel format."""
    
    def __init__(self):
        """Initialize Excel exporter."""
        Config.ensure_directories()
        self.export_dir = Config.EXPORT_DIR
    
    def export_student_list(self, students: List[Student], filename: str = None) -> str:
        """Export list of students to Excel."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lista_estudiantes_{timestamp}.xlsx"
        
        filepath = self.export_dir / filename
        
        # Convert students to list of dictionaries
        data = []
        for student in students:
            data.append({
                'ID': student.id,
                'Nombre': student.nombre,
                'Apellido': student.apellido,
                'DNI': student.dni,
                'Fecha Nacimiento': student.fecha_nacimiento,
                'Email': student.email,
                'Teléfono': student.telefono,
                'Dirección': student.direccion,
                'Ciudad': student.ciudad,
                'Provincia': student.provincia,
                'Código Postal': student.codigo_postal,
                'Contacto Emergencia': student.contacto_emergencia_nombre,
                'Tel. Emergencia': student.contacto_emergencia_telefono,
                'Relación': student.contacto_emergencia_relacion,
                'Instrumento': student.instrumento,
                'Nivel': student.nivel,
                'Experiencia Previa': student.experiencia_previa,
                'Fecha Inscripción': student.fecha_inscripcion,
                'Estado': student.estado,
                'Notas': student.notas
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Export to Excel with formatting
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Inscriptos', index=False)
            
            # Get the worksheet
            worksheet = writer.sheets['Inscriptos']
            
            # Auto-adjust columns width
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format header row
            for cell in worksheet[1]:
                cell.font = cell.font.copy(bold=True)
                cell.fill = cell.fill.copy(fgColor="1a237e")
        
        return str(filepath)
    
    def export_statistics(self, students: List[Student], filename: str = None) -> str:
        """Export statistics about students."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"estadisticas_{timestamp}.xlsx"
        
        filepath = self.export_dir / filename
        
        # Prepare data for different sheets
        
        # 1. General statistics
        total_students = len(students)
        by_status = {}
        by_instrument = {}
        by_level = {}
        by_city = {}
        
        for student in students:
            # By status
            by_status[student.estado] = by_status.get(student.estado, 0) + 1
            # By instrument
            if student.instrumento:
                by_instrument[student.instrumento] = by_instrument.get(student.instrumento, 0) + 1
            # By level
            if student.nivel:
                by_level[student.nivel] = by_level.get(student.nivel, 0) + 1
            # By city
            by_city[student.ciudad] = by_city.get(student.ciudad, 0) + 1
        
        # Create DataFrames
        general_stats = pd.DataFrame([
            {'Métrica': 'Total de Inscriptos', 'Cantidad': total_students}
        ])
        
        status_df = pd.DataFrame([
            {'Estado': k, 'Cantidad': v} for k, v in by_status.items()
        ])
        
        instrument_df = pd.DataFrame([
            {'Instrumento': k, 'Cantidad': v} for k, v in by_instrument.items()
        ])
        
        level_df = pd.DataFrame([
            {'Nivel': k, 'Cantidad': v} for k, v in by_level.items()
        ])
        
        city_df = pd.DataFrame([
            {'Ciudad': k, 'Cantidad': v} for k, v in by_city.items()
        ])
        
        # Export to Excel with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            general_stats.to_excel(writer, sheet_name='General', index=False)
            status_df.to_excel(writer, sheet_name='Por Estado', index=False)
            instrument_df.to_excel(writer, sheet_name='Por Instrumento', index=False)
            level_df.to_excel(writer, sheet_name='Por Nivel', index=False)
            city_df.to_excel(writer, sheet_name='Por Ciudad', index=False)
            
            # Format all sheets
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Format header
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
        
        return str(filepath)
