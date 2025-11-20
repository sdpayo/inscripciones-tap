"""Generador de PDFs (certificados y listados)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pathlib import Path
from datetime import datetime
from config.settings import settings, CERTIFICATES_DIR, BASE_DIR

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
            output_path = CERTIFICATES_DIR / f"certificado_{apellido}_{nombre}_{legajo}_{fecha}.pdf"
        
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
        
        # Nombre completo
        nombre_completo = f"{registro.get('nombre', '')} {registro.get('apellido', '')}"
        c.drawString(margin_left, y, f"Nombre y Apellido: {nombre_completo}")
        y -= 15
        
        # DNI
        dni = registro.get("dni", "N/A")
        c.drawString(margin_left, y, f"DNI: {dni}")
        y -= 15
        
        # Legajo (si no se mostró arriba)
        if legajo_display:
            c.drawString(margin_left, y, f"Legajo: {legajo_display}")
            y -= 15
        
        # Edad
        edad = registro.get("edad", "")
        if edad:
            c.drawString(margin_left, y, f"Edad: {edad}")
            y -= 15
        
        # Domicilio
        domicilio = registro.get("direccion", "") or registro.get("domicilio", "")
        if domicilio:
            c.drawString(margin_left, y, f"Domicilio: {domicilio}")
            y -= 15
        
        # Mail
        mail = registro.get("email", "") or registro.get("mail", "")
        if mail:
            c.drawString(margin_left, y, f"Mail: {mail}")
            y -= 15
        
        y -= 10
        
        # === DATOS DE INSCRIPCIÓN ===
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin_left, y, "Datos de Inscripción:")
        y -= 20
        
        c.setFont("Helvetica", 10)
        
        # Turno
        turno = registro.get("turno", "N/A")
        c.drawString(margin_left, y, f"Turno: {turno}")
        y -= 15
        
        # Año
        anio = registro.get("anio", "") or registro.get("año", "")
        c.drawString(margin_left, y, f"Año: {anio}°")
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
        
        y -= 10
        
        # === INFORMACIÓN ADICIONAL ===
        # Seguro escolar
        seguro = registro.get("seguro_escolar", "No")
        if seguro and seguro.lower() in ("sí", "si", "yes", "s", "1", "true"):
            c.setFont("Helvetica-Bold", 10)
            c.drawString(margin_left, y, "✓ Seguro escolar contratado")
            y -= 15
            c.setFont("Helvetica", 10)
        
        # Obra social
        obra_social = registro.get("obra_social", "")
        if obra_social:
            c.drawString(margin_left, y, f"Obra social: {obra_social}")
            y -= 15
        
        # Pago voluntario
        pago_voluntario = registro.get("pago_voluntario", "No")
        if pago_voluntario and pago_voluntario.lower() in ("sí", "si", "yes", "s", "1", "true"):
            c.setFont("Helvetica-Bold", 10)
            c.drawString(margin_left, y, "✓ Pago voluntario")
            y -= 15
            c.setFont("Helvetica", 10)
            
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
                
                c.drawString(margin_left, y, f"Monto: {monto_formatted}")
                y -= 15
        
        y -= 20
        
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
            "Este certificado es válido con firma y sello de la institución"
        )
        
        # Guardar
        c.save()
        
        return True, str(output_path)
    
    except Exception as e:
        import traceback
        return False, f"Error al generar certificado: {e}\n{traceback.format_exc()}"


def generar_listado_pdf(registros, output_path, filtro_materia=None, filtro_profesor=None):
    """
<<<<<<< HEAD
    Genera listado de inscripciones en PDF con encabezado profesional.
=======
    Genera listado de inscripciones en PDF con logo y encabezado mejorado.
>>>>>>> 35881a2293d81defd7baf5ac87a9f0a29b2d78f3
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
<<<<<<< HEAD
        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # === ENCABEZADO CON LOGO ===
=======
        doc = SimpleDocTemplate(str(output_path), pagesize=landscape(A4),
                                leftMargin=1*cm, rightMargin=1*cm,
                                topMargin=1*cm, bottomMargin=1*cm)
        elements = []
        styles = getSampleStyleSheet()
        
        # === LOGO Y ENCABEZADO ===
>>>>>>> 35881a2293d81defd7baf5ac87a9f0a29b2d78f3
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
        
<<<<<<< HEAD
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
=======
        # Insertar logo si existe
        if logo_path and Path(logo_path).exists():
            try:
                img = Image(logo_path, width=2*cm, height=2*cm)
                img.hAlign = 'LEFT'
                elements.append(img)
                elements.append(Spacer(1, 0.3*cm))
            except Exception as e:
                print(f"[WARN] No se pudo cargar el logo: {e}")
        
        # Nombre de la escuela
        school_style = ParagraphStyle(
            'SchoolStyle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_CENTER,
            spaceAfter=6
        )
        school_name = Paragraph(
            '<b>Escuela Superior de Música N°6003 - "José Lo Giudice"</b>',
            school_style
        )
        elements.append(school_name)
        elements.append(Spacer(1, 0.3*cm))
        
        # Título principal
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            alignment=TA_CENTER,
            spaceAfter=12
        )
        title = Paragraph('<b>LISTADO DE INSCRIPCIONES</b>', title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.4*cm))
        
        # Mostrar filtros aplicados si existen
        filter_text = []
        if filtro_materia and filtro_materia != "(Todas)":
            filter_text.append(f"<b>Materia:</b> {filtro_materia}")
        if filtro_profesor and filtro_profesor != "(Todos)":
            filter_text.append(f"<b>Profesor:</b> {filtro_profesor}")
        
        if filter_text:
            filter_style = ParagraphStyle(
                'FilterStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#555555'),
                alignment=TA_LEFT,
                spaceAfter=6
            )
            filters_para = Paragraph(" | ".join(filter_text), filter_style)
            elements.append(filters_para)
            elements.append(Spacer(1, 0.3*cm))
>>>>>>> 35881a2293d81defd7baf5ac87a9f0a29b2d78f3
        
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
<<<<<<< HEAD
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
=======
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_LEFT,
            spaceAfter=6
        )
        info = Paragraph(f"<b>Generado:</b> {fecha} | <b>Total:</b> {len(registros)} inscripciones", info_style)
        elements.append(info)
        elements.append(Spacer(1, 0.5*cm))
        
        # === TABLA DE DATOS MEJORADA ===
        # Headers
        headers = ['Nombre', 'Apellido', 'DNI', 'Materia', 'Profesor', 'Comisión', 'Turno', 'Año']
>>>>>>> 35881a2293d81defd7baf5ac87a9f0a29b2d78f3
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
<<<<<<< HEAD

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
=======
        
        # Crear tabla con estilo mejorado
        table = Table(data, colWidths=[3*cm, 3*cm, 2.5*cm, 5.5*cm, 4*cm, 2*cm, 2.5*cm, 1.5*cm])
        table.setStyle(TableStyle([
            # Headers - Estilo mejorado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Cuerpo - Estilo mejorado
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1a1a1a')),
            ('ALIGN', (0, 1), (2, -1), 'LEFT'),  # Nombre, Apellido, DNI a la izquierda
            ('ALIGN', (3, 1), (-1, -1), 'LEFT'),  # Resto a la izquierda
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2c5aa0')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2c5aa0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternar colores de filas - más sutil
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
>>>>>>> 35881a2293d81defd7baf5ac87a9f0a29b2d78f3
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