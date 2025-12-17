"""Generador de PDFs (certificados y listados)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pathlib import Path
from datetime import datetime
from config.settings import settings, CERTIFICATES_DIR, BASE_DIR

# Constantes
MAX_CHARS_PER_LINE = 80  # Máximo de caracteres por línea en observaciones

def _get_unique_pdf_path(base_path):
    """Genera un path único para PDF agregando número si ya existe."""
    path = Path(base_path)
    if not path.exists():
        return path
    
    # Si existe, agregar número
    stem = path.stem
    ext = path.suffix
    parent = path.parent
    counter = 1
    
    while True:
        new_path = parent / f"{stem}_{counter}{ext}"
        if not new_path.exists():
            return new_path
        counter += 1


def generar_certificado_pdf(registro, output_path=None):
    """
    Genera certificado de inscripción en PDF con logo y firma.
    Args:
        registro (dict): Datos del alumno
        output_path (str, optional): Ruta de salida
    Returns:
        tuple(bool, str): (exito, ruta_archivo)
    """
    try:
        # Validar datos mínimos
        if not registro.get("nombre") or not registro.get("apellido"):
            return False, "Faltan datos del alumno"
        
        # Generar nombre de archivo
        if not output_path:
            apellido = registro.get("apellido", "").replace(" ", "_")
            nombre = registro.get("nombre", "").replace(" ", "_")
            legajo = registro.get("legajo", registro.get("dni", ""))
            fecha = datetime.now().strftime("%Y%m%d")
            
            CERTIFICATES_DIR.mkdir(parents=True, exist_ok=True)
            base_path = CERTIFICATES_DIR / f"certificado_{apellido}_{nombre}_{legajo}_{fecha}.pdf"
            output_path = _get_unique_pdf_path(base_path)
        
        # Crear PDF
        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4
        
        # Márgenes
        margin_left = 50
        margin_right = 50
        margin_top = 50
        
        # === ENCABEZADO CON LOGO ===
        y = height - margin_top
        
        # Logo (izquierda arriba)
        logo_path = settings.get("pdf.logo_path", "")
        if not logo_path:
            # Buscar logo en varias ubicaciones posibles
            possible_logos = [
                BASE_DIR / "ESM_Alta.jpg",
                BASE_DIR / "data" / "ESM_Alta.jpg",
                BASE_DIR / "assets" / "ESM_Alta.jpg"
            ]
            for p in possible_logos:
                if p.exists():
                    logo_path = str(p)
                    break
        
        logo_width = 80
        logo_height = 80
        
        if logo_path and Path(logo_path).exists():
            try:
                c.drawImage(
                    logo_path, 
                    margin_left, 
                    y - logo_height, 
                    width=logo_width, 
                    height=logo_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception as e:
                print(f"[WARN] No se pudo cargar el logo: {e}")
        
        # Título a la derecha del logo
        text_x = margin_left + logo_width + 15
        c.setFont("Helvetica-Bold", 11)
        c.drawString(text_x, y - 15, "Certificado de Inscripción - Escuela Superior de Música")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(text_x, y - 30, 'N°6003 - "José Lo Giudice"')
        
        legajo_display = registro.get("legajo", "")
        if legajo_display:
            c.setFont("Helvetica", 9)
            c.drawString(text_x, y - 45, f"Legajo: {legajo_display}")
        
        y = y - logo_height - 20
        
        # Línea separadora
        c.setLineWidth(0.5)
        c.line(margin_left, y, width - margin_right, y)
        y -= 20
        
        # === TÍTULO PRINCIPAL ===
        c.setFont("Helvetica-Bold", 16)
        title = "CERTIFICADO DE INSCRIPCIÓN"
        title_width = c.stringWidth(title, "Helvetica-Bold", 16)
        c.drawString((width - title_width) / 2, y, title)
        y -= 30
        
        # === DATOS DEL ESTUDIANTE ===
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin_left, y, "Datos del Estudiante:")
        y -= 20
        
        c.setFont("Helvetica", 10)
        
        # Nombre completo - Formato especial: "APELLIDO, Nombre"
        apellido_upper = registro.get('apellido', '').upper()
        # Capitalizar cada palabra del nombre manteniendo mayúsculas iniciales
        nombre_parts = registro.get('nombre', '').split()
        nombre_normal = ' '.join(word.capitalize() for word in nombre_parts)
        nombre_completo = f"{apellido_upper}, {nombre_normal}"
        c.drawString(margin_left, y, f"Nombre y Apellido: {nombre_completo}")
        y -= 15
        
        # DNI
        dni = registro.get("dni", "N/A")
        c.drawString(margin_left, y, f"DNI: {dni}")
        y -= 15
        
        # Fecha de nacimiento
        fecha_nac = registro.get("fecha_nacimiento", "")
        if fecha_nac:
            c.drawString(margin_left, y, f"Fecha de Nacimiento: {fecha_nac}")
            y -= 15
        
        # Edad
        edad = registro.get("edad", "")
        if edad:
            c.drawString(margin_left, y, f"Edad: {edad}")
            y -= 15
        
        # Legajo
        if legajo_display:
            c.drawString(margin_left, y, f"Legajo: {legajo_display}")
            y -= 15
        
        # Domicilio
        domicilio = registro.get("direccion", "") or registro.get("domicilio", "")
        if domicilio:
            c.drawString(margin_left, y, f"Domicilio: {domicilio}")
            y -= 15
        
        # Teléfono
        telefono = registro.get("telefono", "")
        if telefono:
            c.drawString(margin_left, y, f"Teléfono: {telefono}")
            y -= 15
        
        # Mail
        mail = registro.get("email", "") or registro.get("mail", "")
        if mail:
            c.drawString(margin_left, y, f"Mail: {mail}")
            y -= 15
        
        y -= 10
        
        # === DATOS DE PADRES/TUTORES ===
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin_left, y, "Datos de Padres/Tutores:")
        y -= 20
        
        c.setFont("Helvetica", 10)
        
        # Nombre del padre
        nombre_padre = registro.get("nombre_padre", "")
        if nombre_padre:
            c.drawString(margin_left, y, f"Nombre del Padre: {nombre_padre}")
            y -= 15
        
        # Nombre de la madre
        nombre_madre = registro.get("nombre_madre", "")
        if nombre_madre:
            c.drawString(margin_left, y, f"Nombre de la Madre: {nombre_madre}")
            y -= 15
        
        # Teléfono de emergencia
        telefono_emerg = registro.get("telefono_emergencia", "")
        if telefono_emerg:
            c.drawString(margin_left, y, f"Teléfono de Emergencia: {telefono_emerg}")
            y -= 15
        
        y -= 10
        
        # === DATOS DE INSCRIPCIÓN ===
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin_left, y, "Datos de Inscripción:")
        y -= 20
        
        c.setFont("Helvetica", 10)
        
        # Año
        anio = registro.get("anio", "") or registro.get("año", "")
        if anio:
            c.drawString(margin_left, y, f"Año: {anio}°")
            y -= 15
        
        # Turno
        turno = registro.get("turno", "N/A")
        c.drawString(margin_left, y, f"Turno: {turno}")
        y -= 15
        
        # Materia
        materia = registro.get("materia", "N/A")
        # Si la materia es muy larga, cortarla o usar multi-línea
        if len(materia) > 70:
            c.drawString(margin_left, y, f"Materia: {materia[:70]}")
            y -= 15
            c.drawString(margin_left + 60, y, materia[70:])
            y -= 15
        else:
            c.drawString(margin_left, y, f"Materia: {materia}")
            y -= 15
        
        # Profesor/a
        profesor = registro.get("profesor", "N/A")
        c.drawString(margin_left, y, f"Profesor/a: {profesor}")
        y -= 15
        
        # Comisión
        comision = registro.get("comision", "N/A")
        c.drawString(margin_left, y, f"Comisión: {comision}")
        y -= 15
        
        # Horario (si existe)
        horario = registro.get("horario", "")
        if horario:
            c.drawString(margin_left, y, f"Horario: {horario}")
            y -= 15
        
        # En lista de espera
        en_lista_espera = registro.get("en_lista_espera", "No")
        if en_lista_espera and en_lista_espera.lower() in ("sí", "si", "yes", "s", "1", "true"):
            c.setFont("Helvetica-Bold", 10)
            c.drawString(margin_left, y, "⚠ EN LISTA DE ESPERA")
            c.setFont("Helvetica", 10)
            y -= 15
        
        y -= 10
        
        # === INFORMACIÓN ADICIONAL ===
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin_left, y, "Información Adicional:")
        y -= 20
        
        c.setFont("Helvetica", 10)
        
        # SAETA
        saeta = registro.get("saeta", "")
        if saeta:
            c.drawString(margin_left, y, f"SAETA: {saeta}")
            y -= 15
        
        # Obra social
        obra_social = registro.get("obra_social", "")
        if obra_social:
            c.drawString(margin_left, y, f"Obra Social: {obra_social}")
            y -= 15
        
        # Seguro escolar
        seguro = registro.get("seguro_escolar", "No")
        if seguro:
            c.drawString(margin_left, y, f"Seguro Escolar: {seguro}")
            y -= 15
        
        # Pago voluntario
        pago_voluntario = registro.get("pago_voluntario", "No")
        if pago_voluntario:
            c.drawString(margin_left, y, f"Pago Voluntario: {pago_voluntario}")
            y -= 15
            
            # Mostrar monto si existe
            monto = registro.get("monto", "")
            if monto:
                # Formatear monto como moneda
                try:
                    # Intentar convertir a número y formatear
                    if isinstance(monto, str):
                        # Remover caracteres no numéricos excepto punto y coma
                        monto_clean = monto.replace("$", "").replace(",", "").strip()
                        if monto_clean:
                            monto_num = float(monto_clean)
                            monto_formatted = f"${monto_num:,.2f}"
                        else:
                            monto_formatted = monto
                    else:
                        monto_num = float(monto)
                        monto_formatted = f"${monto_num:,.2f}"
                except (ValueError, TypeError):
                    # Si no se puede convertir, usar el valor original
                    monto_formatted = f"${monto}"
                
                c.drawString(margin_left, y, f"  Monto: {monto_formatted}")
                y -= 15
        
        # Permiso
        permiso = registro.get("permiso", "")
        if permiso:
            c.drawString(margin_left, y, f"Permiso: {permiso}")
            y -= 15
        
        # Observaciones (puede ser largo, hay que manejarlo especialmente)
        observaciones = registro.get("observaciones", "")
        if observaciones:
            c.drawString(margin_left, y, f"Observaciones:")
            y -= 15
            # Dividir observaciones en líneas si es muy largo
            obs_lines = []
            while len(observaciones) > MAX_CHARS_PER_LINE:
                split_pos = observaciones[:MAX_CHARS_PER_LINE].rfind(' ')
                if split_pos == -1:
                    split_pos = MAX_CHARS_PER_LINE
                obs_lines.append(observaciones[:split_pos])
                observaciones = observaciones[split_pos:].strip()
            if observaciones:
                obs_lines.append(observaciones)
            
            for line in obs_lines:
                c.drawString(margin_left + 10, y, line)
                y -= 15
        
        y -= 10
        
        # === FECHAS ===
        c.setFont("Helvetica", 9)
        
        # Fecha de emisión
        fecha_emision = datetime.now().strftime("%d/%m/%Y")
        c.drawString(margin_left, y, f"Emitido el {fecha_emision}")
        y -= 12
        
        # Fecha de inscripción
        fecha_insc = registro.get("fecha_inscripcion", "")
        if fecha_insc:
            try:
                # Intentar formatear la fecha
                if "T" in fecha_insc:
                    fecha_insc = fecha_insc.split("T")[0]
                fecha_insc_formatted = datetime.fromisoformat(fecha_insc.replace(" ", "T")).strftime("%d/%m/%Y")
            except:
                fecha_insc_formatted = fecha_insc[:10] if len(fecha_insc) >= 10 else fecha_insc
            
            c.drawString(margin_left, y, f"Fecha de inscripción: {fecha_insc_formatted}")
            y -= 12
        
        # === PIE DE PÁGINA ===
        y_footer = 150
        
        # Buscar imagen de firma
        firma_path = settings.get("pdf.firma_path", "")
        if not firma_path:
            # Buscar firma en varias ubicaciones
            possible_firmas = [
                BASE_DIR / "firma.png",
                BASE_DIR / "data" / "firma.png",
                BASE_DIR / "assets" / "firma.png"
            ]
            for p in possible_firmas:
                if p.exists():
                    firma_path = str(p)
                    break
        
        # Insertar imagen de firma si existe
        if firma_path and Path(firma_path).exists():
            try:
                firma_width = 120
                firma_height = 40
                firma_x = width - margin_right - firma_width - 20
                
                c.drawImage(
                    firma_path,
                    firma_x,
                    y_footer + 20,
                    width=firma_width,
                    height=firma_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception as e:
                print(f"[WARN] No se pudo cargar la firma: {e}")
        
        # Línea para firma
        line_y = y_footer + 15
        line_start = width - margin_right - 180
        line_end = width - margin_right - 20
        c.line(line_start, line_y, line_end, line_y)
        
        # Texto debajo de la línea
        c.setFont("Helvetica", 9)
        text_x = (line_start + line_end) / 2
        
        c.drawCentredString(text_x, line_y - 12, "Firma y Sello")
        c.drawCentredString(text_x, line_y - 24, "Autoridad Escolar")
        
        # Texto rector (si querés agregarlo)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(text_x, line_y - 38, "Prof. José Néstor Mevorás Lencinas")
        c.setFont("Helvetica", 8)
        c.drawCentredString(text_x, line_y - 50, "Rector Escuela Superior de Música \"José Lo Giudice\"")
        c.drawCentredString(text_x, line_y - 62, "IES Nº 6003")
        
        # Pie de página legal
        c.setFont("Helvetica", 7)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawCentredString(
            width / 2, 
            30, 
            "Sirva la presente constancia de inscripción como único recibo de pago"
        )
        
        # Guardar
        c.save()
        
        return True, str(output_path)
    
    except Exception as e:
        import traceback
        return False, f"Error al generar certificado: {e}\n{traceback.format_exc()}"


def generar_listado_pdf(registros, output_path, filtro_materia=None, filtro_profesor=None):
    """
    Genera listado de inscripciones en PDF con encabezado profesional.
    Args:
        registros (list): Lista de registros
        output_path (str): Ruta de salida
        filtro_materia (str, optional): Materia filtrada
        filtro_profesor (str, optional): Profesor filtrado
    Returns:
        tuple(bool, str): (exito, mensaje)
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
                # Crear nombre de archivo dinámicamente

                # Bloque NUEVO a agregar:
        if not output_path or output_path in ("", " "):
            nombre = (f"{(filtro_materia or 'Materia').strip()}_{(filtro_profesor or 'Profesor').strip()}_Lista.pdf"
                      .replace(" ", "_")
                      .replace("/", "_"))
            output_path = nombre

        # Crear PDF en horizontal
        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # === ENCABEZADO CON LOGO ===
        # Buscar logo
        logo_path = settings.get("pdf.logo_path", "")
        if not logo_path:
            possible_logos = [
                BASE_DIR / "ESM_Alta.jpg",
                BASE_DIR / "data" / "ESM_Alta.jpg",
                BASE_DIR / "assets" / "ESM_Alta.jpg"
            ]
            for p in possible_logos:
                if p.exists():
                    logo_path = str(p)
                    break
        
        # Agregar logo si existe
        if logo_path and Path(logo_path).exists():
            try:
                img = Image(logo_path, width=3*cm, height=3*cm)
                elements.append(img)
                elements.append(Spacer(1, 0.3*cm))
            except Exception as e:
                print(f"[WARN] No se pudo cargar logo en PDF: {e}")
        
        # Título institucional
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#003366'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph("Escuela Superior de Música N°6003", title_style)
        subtitle = Paragraph('"José Lo Giudice"', subtitle_style)
        elements.append(title)
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3*cm))
        
        # Título del listado
        listado_title_style = ParagraphStyle(
            'ListadoTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.black,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        listado_title = Paragraph("LISTADO DE INSCRIPCIONES", listado_title_style)
        elements.append(listado_title)
        elements.append(Spacer(1, 0.3*cm))
        
        # Info de filtros aplicados
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        )
        
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        info_lines = [f"<b>Fecha de generación:</b> {fecha}"]
        info_lines.append(f"<b>Total de inscripciones:</b> {len(registros)}")
        
        if filtro_materia and filtro_materia != "(Todas)":
            info_lines.append(f"<b>Materia:</b> {filtro_materia}")
        
        if filtro_profesor and filtro_profesor != "(Todos)":
            info_lines.append(f"<b>Profesor/a:</b> {filtro_profesor}")
        
        for line in info_lines:
            elements.append(Paragraph(line, info_style))
        
        elements.append(Spacer(1, 0.5*cm))
        
        # === TABLA DE DATOS ===
        # Ordenar registros por apellido (A-Z)
        registros = sorted(registros, key=lambda x: x.get('apellido', '').lower())

        # Encabezado: Apellido es la primera columna
        headers = ['Apellido', 'Nombre', 'DNI', 'Mail', 'Legajo', 'Com', 'Turno', 'Año'] #'Materia', 'Profesor',
        data = [headers]

        # Construir las filas
        for reg in registros:
            row = [
                reg.get('apellido', '')[:15],
                reg.get('nombre', '')[:15],
                reg.get('dni', ''),
                reg.get('email', '')[:30] or reg.get('mail', '')[:30],
                reg.get('legajo', '')[:15],
                #reg.get('materia', '')[:30],
                #reg.get('profesor', '')[:20],
                reg.get('comision', ''),
                reg.get('turno', '')[:10],
                reg.get('anio', '') or reg.get('año', '')
            ]
            data.append(row)

        # Crear tabla
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            # Headers
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Cuerpo
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternar colores de filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),
        ]))
        
        elements.append(table)
        
        # Pie de página
        elements.append(Spacer(1, 0.5*cm))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        footer = Paragraph("Documento generado automáticamente por el Sistema de Inscripciones TAP", footer_style)
        elements.append(footer)
        
        # Generar PDF
        doc.build(elements)
        
        return True, f"Listado generado:\n{output_path}"
    
    except ImportError:
        return False, "Falta instalar reportlab: pip install reportlab"
    except Exception as e:
        import traceback
        return False, f"Error al generar listado: {e}\n{traceback.format_exc()}"