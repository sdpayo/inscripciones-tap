# test_pdf.py
from services.pdf_generator import generar_certificado_pdf
from datetime import datetime

registro_test = {
    "id": "TEST001",
    "legajo": "TEST001",
    "nombre": "Juan Carlos",
    "apellido": "Pérez López",
    "dni": "12.345.678",
    "edad": "25",
    "domicilio": "Calle Falsa 123",
    "mail": "juan@example.com",
    "turno": "Mañana",
    "anio": "2",
    "materia": "Piano",
    "profesor": "Prof. María García",
    "comision": "A",
    "seguro_escolar": "SI",
    "pago_voluntario": "SI",
    "monto": "5000.50",
    "observaciones": "Estudiante destacado",
    "fecha_inscripcion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

ok, resultado = generar_certificado_pdf(registro_test)
if ok:
    print(f"✅ PDF generado: {resultado}")
    import os
    os.startfile(resultado) if os.name == 'nt' else os.system(f"open '{resultado}'")
else:
    print(f"❌ Error: {resultado}")