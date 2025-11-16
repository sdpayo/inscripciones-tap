"""PDF export functionality."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from pathlib import Path
from typing import List
from ..models import Student
from ..config import Config


class PDFExporter:
    """Export data to PDF format."""
    
    def __init__(self):
        """Initialize PDF exporter."""
        Config.ensure_directories()
        self.export_dir = Config.EXPORT_DIR
    
    def export_student_list(self, students: List[Student], filename: str = None) -> str:
        """Export list of students to PDF."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lista_estudiantes_{timestamp}.pdf"
        
        filepath = self.export_dir / filename
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Add title
        title = Paragraph(f"{Config.SCHOOL_NAME}<br/>{Config.PROGRAM_NAME}<br/>Lista de Inscriptos", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add date
        date_text = Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal'])
        elements.append(date_text)
        elements.append(Spacer(1, 0.2*inch))
        
        # Create table data
        data = [['N°', 'Nombre', 'DNI', 'Instrumento', 'Email', 'Teléfono', 'Estado']]
        
        for idx, student in enumerate(students, 1):
            data.append([
                str(idx),
                student.get_full_name(),
                student.dni,
                student.instrumento or '-',
                student.email,
                student.telefono,
                student.estado
            ])
        
        # Create table
        table = Table(data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 1.2*inch, 1.8*inch, 1*inch, 1*inch])
        
        # Add style to table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        
        # Add footer
        elements.append(Spacer(1, 0.3*inch))
        footer_text = Paragraph(f"Total de inscriptos: {len(students)}", styles['Normal'])
        elements.append(footer_text)
        
        # Build PDF
        doc.build(elements)
        
        return str(filepath)
    
    def generate_certificate(self, student: Student, filename: str = None) -> str:
        """Generate a certificate for a student."""
        if not filename:
            filename = f"certificado_{student.dni}.pdf"
        
        filepath = self.export_dir / filename
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CertTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Body style
        body_style = ParagraphStyle(
            'CertBody',
            parent=styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        # Add spacing
        elements.append(Spacer(1, 1.5*inch))
        
        # Add certificate title
        title = Paragraph("CERTIFICADO DE INSCRIPCIÓN", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        # Add school info
        school_info = Paragraph(
            f"<b>{Config.SCHOOL_NAME}</b><br/>{Config.PROGRAM_NAME}",
            body_style
        )
        elements.append(school_info)
        elements.append(Spacer(1, 0.5*inch))
        
        # Certificate text
        cert_text = Paragraph(
            f"Se certifica que <b>{student.get_full_name()}</b><br/>"
            f"DNI: <b>{student.dni}</b><br/><br/>"
            f"Ha completado su inscripción al programa<br/>"
            f"<b>{Config.PROGRAM_NAME}</b><br/><br/>"
            f"Instrumento: <b>{student.instrumento or 'No especificado'}</b><br/>"
            f"Nivel: <b>{student.nivel or 'No especificado'}</b>",
            body_style
        )
        elements.append(cert_text)
        elements.append(Spacer(1, 1*inch))
        
        # Add date
        date_text = Paragraph(
            f"Fecha de inscripción: {student.fecha_inscripcion}",
            styles['Normal']
        )
        date_text.alignment = TA_CENTER
        elements.append(date_text)
        
        # Build PDF
        doc.build(elements)
        
        return str(filepath)
    
    def export_student_detail(self, student: Student, filename: str = None) -> str:
        """Export detailed student information to PDF."""
        if not filename:
            filename = f"ficha_{student.dni}.pdf"
        
        filepath = self.export_dir / filename
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'DetailTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        title = Paragraph("FICHA DE INSCRIPCIÓN", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Student data
        data = [
            ['Campo', 'Información'],
            ['Nombre completo', student.get_full_name()],
            ['DNI', student.dni],
            ['Fecha de nacimiento', student.fecha_nacimiento],
            ['Email', student.email],
            ['Teléfono', student.telefono],
            ['Dirección', student.direccion],
            ['Ciudad', student.ciudad],
            ['Provincia', student.provincia],
            ['Código Postal', student.codigo_postal or '-'],
            ['', ''],
            ['Contacto de emergencia', student.contacto_emergencia_nombre or '-'],
            ['Teléfono de emergencia', student.contacto_emergencia_telefono or '-'],
            ['Relación', student.contacto_emergencia_relacion or '-'],
            ['', ''],
            ['Instrumento', student.instrumento or '-'],
            ['Nivel', student.nivel or '-'],
            ['Experiencia previa', student.experiencia_previa or '-'],
            ['', ''],
            ['Fecha de inscripción', student.fecha_inscripcion],
            ['Estado', student.estado],
            ['Notas', student.notas or '-'],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        
        return str(filepath)
