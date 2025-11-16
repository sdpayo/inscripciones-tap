"""Test comprehensivo para generación de certificados PDF."""
from services.pdf_generator import generar_certificado_pdf
from datetime import datetime
import os

def test_certificado_completo():
    """Test con todos los datos."""
    registro = {
        "nombre": "Juan Carlos",
        "apellido": "Pérez López",
        "dni": "12.345.678",
        "legajo": "TEST001",
        "edad": "25",
        "direccion": "Calle Falsa 123",
        "email": "juan@example.com",
        "turno": "Mañana",
        "anio": "2",
        "materia": "Piano",
        "profesor": "Prof. María García",
        "comision": "A",
        "horario": "8:00 - 10:00",
        "seguro_escolar": "Sí",
        "obra_social": "OSDE",
        "fecha_inscripcion": "2025-11-16T21:17:25"
    }
    
    ok, resultado = generar_certificado_pdf(registro)
    if ok:
        print(f"✅ Test completo: {resultado}")
        assert os.path.exists(resultado), "El archivo PDF no existe"
        # Verificar formato de nombre
        assert "Pérez_López_Juan_Carlos" in resultado, f"Nombre incorrecto en: {resultado}"
        assert "TEST001" in resultado, "Legajo no aparece en nombre"
    else:
        print(f"❌ Test completo falló: {resultado}")
        return False
    return True

def test_certificado_datos_minimos():
    """Test con datos mínimos requeridos."""
    registro = {
        "nombre": "María",
        "apellido": "González",
        "dni": "98765432",
        "turno": "Tarde",
        "materia": "Guitarra"
    }
    
    ok, resultado = generar_certificado_pdf(registro)
    if ok:
        print(f"✅ Test mínimo: {resultado}")
        assert os.path.exists(resultado), "El archivo PDF no existe"
        assert "González_María" in resultado, f"Nombre incorrecto en: {resultado}"
    else:
        print(f"❌ Test mínimo falló: {resultado}")
        return False
    return True

def test_certificado_fecha_con_espacio():
    """Test con fecha en formato con espacio."""
    registro = {
        "nombre": "Pedro",
        "apellido": "Ramírez",
        "dni": "11223344",
        "turno": "Noche",
        "materia": "Canto",
        "fecha_inscripcion": "2025-11-16 14:30:00"
    }
    
    ok, resultado = generar_certificado_pdf(registro)
    if ok:
        print(f"✅ Test fecha con espacio: {resultado}")
        assert os.path.exists(resultado), "El archivo PDF no existe"
    else:
        print(f"❌ Test fecha con espacio falló: {resultado}")
        return False
    return True

def test_certificado_materia_larga():
    """Test con materia muy larga."""
    registro = {
        "nombre": "Ana",
        "apellido": "Martínez",
        "dni": "55667788",
        "turno": "Mañana",
        "materia": "Introducción a la Teoría Musical Avanzada con Práctica Instrumental y Análisis Compositivo"
    }
    
    ok, resultado = generar_certificado_pdf(registro)
    if ok:
        print(f"✅ Test materia larga: {resultado}")
        assert os.path.exists(resultado), "El archivo PDF no existe"
    else:
        print(f"❌ Test materia larga falló: {resultado}")
        return False
    return True

def test_certificado_sin_logo_ni_firma():
    """Test cuando no existen archivos de logo y firma."""
    from config.settings import settings
    
    # Temporalmente setear paths inválidos
    original_logo = settings.get("pdf.logo_path", "")
    original_firma = settings.get("pdf.firma_path", "")
    
    settings.set("pdf.logo_path", "/tmp/no_existe_logo.jpg")
    settings.set("pdf.firma_path", "/tmp/no_existe_firma.png")
    
    registro = {
        "nombre": "Luis",
        "apellido": "Fernández",
        "dni": "99887766",
        "turno": "Tarde",
        "materia": "Violín"
    }
    
    ok, resultado = generar_certificado_pdf(registro)
    
    # Restaurar configuración (siempre, incluso si estaba vacío)
    settings.set("pdf.logo_path", original_logo)
    settings.set("pdf.firma_path", original_firma)
    
    if ok:
        print(f"✅ Test sin logo/firma: {resultado}")
        assert os.path.exists(resultado), "El archivo PDF no existe"
    else:
        print(f"❌ Test sin logo/firma falló: {resultado}")
        return False
    return True

def test_certificado_campos_alternativos():
    """Test con nombres de campos alternativos (domicilio vs direccion, mail vs email)."""
    registro = {
        "nombre": "Carlos",
        "apellido": "Rodríguez",
        "dni": "44556677",
        "turno": "Mañana",
        "materia": "Batería",
        "domicilio": "Av. Principal 456",  # En vez de 'direccion'
        "mail": "carlos@test.com",  # En vez de 'email'
        "año": "3",  # En vez de 'anio'
    }
    
    ok, resultado = generar_certificado_pdf(registro)
    if ok:
        print(f"✅ Test campos alternativos: {resultado}")
        assert os.path.exists(resultado), "El archivo PDF no existe"
    else:
        print(f"❌ Test campos alternativos falló: {resultado}")
        return False
    return True

if __name__ == "__main__":
    print("="*60)
    print("TESTS COMPREHENSIVOS DE GENERACIÓN DE CERTIFICADOS PDF")
    print("="*60)
    
    tests = [
        ("Certificado completo", test_certificado_completo),
        ("Certificado datos mínimos", test_certificado_datos_minimos),
        ("Certificado fecha con espacio", test_certificado_fecha_con_espacio),
        ("Certificado materia larga", test_certificado_materia_larga),
        ("Certificado sin logo/firma", test_certificado_sin_logo_ni_firma),
        ("Certificado campos alternativos", test_certificado_campos_alternativos),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Ejecutando: {name}")
        print(f"{'='*60}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Excepción en {name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"RESUMEN: {passed} passed, {failed} failed")
    print(f"{'='*60}")
