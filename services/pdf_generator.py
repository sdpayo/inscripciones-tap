"""Generador de PDFs (certificados y listados)."""
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pathlib import Path
from datetime import datetime
from config.settings import settings, CERTIFICATES_DIR

def generar_certificado_pdf(registro, output_path=None):
    """
    Genera certificado de inscripción en PDF.
    Args:
        registro (dict): Datos del alumno
        output_path (str, optional): Ruta de salida
    Returns:
        tuple(bool, str): (exito, mensaje)
    """
    try:
        # Validar datos mínimos
        if not registro.get("nombre") or not registro.get("apellido"):
            return False, "Faltan datos del alumno"
        
        # Generar nombre de archivo
        if not output_path:
            nombre = registro.get("apellido", "").replace(" ", "_")
            apellido = registro.get("nombre", "").replace(" ", "_")
            dni = registro.get("dni", "")
            fecha = datetime.now().strftime("%Y%m%d")
            
            CERTIFICATES_DIR.mkdir(parents=True, exist_ok=True)
            output_path = CERTIFICATES_DIR / f"certificado_{nombre}_{apellido}_{dni}_{fecha}.pdf"
        
        # Crear PDF
        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4
        
        # === ENCABEZADO ===
        # Logo (si existe)
        logo_path = settings.get("pdf.logo_path", "")
        if logo_path and Path(logo_path).exists():
            try:
                c.drawImage(logo_path, 50, height - 100, width=100, height=80, preserveAspectRatio=True)
            except:
                pass
        
        # Título institución
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - 60, "Escuela Superior de Música N°6003")
        
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, height - 80, "Tecnicatura de Acompañamiento en Piano")
        
        # Línea separadora
        c.line(50, height - 100, width - 50, height - 100)
        
        # === TÍTULO CERTIFICADO ===
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width / 2, height - 150, "CERTIFICADO DE INSCRIPCIÓN")
        
        # === DATOS DEL ALUMNO ===
        y = height - 200
        c.setFont("Helvetica", 12)
        
        # Texto introductorio
        c.drawString(80, y, "La Escuela Superior de Música N°6003 certifica que:")
        y -= 40
        
        # Nombre completo
        nombre_completo = f"{registro.get('nombre', '')} {registro.get('apellido', '')}"
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, y, nombre_completo.upper())
        y -= 10
        c.line(150, y, width - 150, y)
        y -= 30
        
        # DNI
        c.setFont("Helvetica", 12)
        dni_text = f"DNI: {registro.get('dni', 'N/A')}"
        c.drawCentredString(width / 2, y, dni_text)
        y -= 40
        
        # Texto descriptivo
        c.drawString(80, y, "Se encuentra inscripto/a en:")
        y -= 30
        
        # === DATOS DE LA INSCRIPCIÓN ===
        c.setFont("Helvetica-Bold", 13)
        
        # Materia
        materia = registro.get("materia", "N/A")
        c.drawString(100, y, f"Materia: {materia}")
        y -= 25
        
        # Profesor
        c.setFont("Helvetica", 12)
        profesor = registro.get("profesor", "N/A")
        c.drawString(100, y, f"Profesor/a: {profesor}")
        y -= 20
        
        # Comisión
        comision = registro.get("comision", "N/A")
        c.drawString(100, y, f"Comisión: {comision}")
        y -= 20
        
        # Turno
        turno = registro.get("turno", "N/A")
        c.drawString(100, y, f"Turno: {turno}")
        y -= 20
        
        # Año
        anio = registro.get("anio", "N/A")
        c.drawString(100, y, f"Año: {anio}°")
        y -= 20
        
        # Horario (si existe)
        horario = registro.get("horario", "")
        if horario:
            c.drawString(100, y, f"Horario: {horario}")
            y -= 20
        
        # === INFORMACIÓN ADICIONAL ===
        y -= 20
        
        # Seguro escolar
        seguro = registro.get("seguro_escolar", "No")
        if seguro == "Sí":
            c.setFont("Helvetica-Bold", 11)
            c.drawString(100, y, "✓ Seguro escolar contratado")
            y -= 20
        
        # Obra social
        obra_social = registro.get("obra_social", "")
        if obra_social:
            c.setFont("Helvetica", 11)
            c.drawString(100, y, f"Obra social: {obra_social}")
            y -= 20
        
        # === FECHA Y FIRMA ===
        y = 150
        
        # Fecha de emisión
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        c.setFont("Helvetica", 11)
        c.drawString(80, y, f"Fecha de emisión: {fecha_hoy}")
        
        # Fecha de inscripción
        fecha_insc = registro.get("fecha_inscripcion", "")
        if fecha_insc:
            fecha_insc_formatted = fecha_insc[:10]
            c.drawString(80, y - 20, f"Fecha de inscripción: {fecha_insc_formatted}")
        
        # Línea para firma
        y = 100
        c.line(width - 250, y, width - 80, y)
        c.setFont("Helvetica", 10)
        c.drawCentredString(width - 165, y - 15, "Firma y Sello")
        c.drawCentredString(width - 165, y - 30, "Autoridad Escolar")
        
        # === PIE DE PÁGINA ===
        c.setFont("Helvetica", 8)
        c.drawCentredString(width / 2, 30, "Este certificado es válido con firma y sello de la institución")
        
        # Guardar
        c.save()
        
        return True, f"Certificado generado:\n{output_path}"
    
    except Exception as e:
        return False, f"Error al generar certificado: {e}"


def generar_listado_pdf(registros, output_path):
    """
    Genera listado de inscripciones en PDF.
    Args:
        registros (list): Lista de registros
        output_path (str): Ruta de salida
    Returns:
        tuple(bool, str): (exito, mensaje)
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        
        # Crear PDF en horizontal
        doc = SimpleDocTemplate(str(output_path), pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title = Paragraph("<b>Listado de Inscripciones</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Info general
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        info = Paragraph(f"Generado: {fecha} | Total: {len(registros)} inscripciones", styles['Normal'])
        elements.append(info)
        elements.append(Spacer(1, 0.5*cm))
        
        # Tabla de datos
        # Headers
        headers = ['Nombre', 'Apellido', 'DNI', 'Materia', 'Profesor', 'Comisión', 'Turno', 'Año']
        data = [headers]
        
        # Filas
        for reg in registros:
            row = [
                reg.get('nombre', '')[:15],  # Truncar para que entre
                reg.get('apellido', '')[:15],
                reg.get('dni', ''),
                reg.get('materia', '')[:30],
                reg.get('profesor', '')[:20],
                reg.get('comision', ''),
                reg.get('turno', '')[:10],
                reg.get('anio', '')
            ]
            data.append(row)
        
        # Crear tabla
        table = Table(data)
        table.setStyle(TableStyle([
            # Headers
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Cuerpo
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternar colores de filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        
        # Generar PDF
        doc.build(elements)
        
        return True, f"Listado generado:\n{output_path}"
    
    except ImportError:
        return False, "Falta instalar reportlab: pip install reportlab"
    except Exception as e:
        return False, f"Error al generar listado: {e}"