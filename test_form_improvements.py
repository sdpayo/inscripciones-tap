"""Tests para las mejoras del formulario de inscripción."""
import sys
from datetime import datetime
from database.csv_handler import generar_id, contar_inscripciones_materia
from models.materias import get_turnos_disponibles, get_info_completa


def test_id_format_underscore():
    """Test: ID con formato de guiones bajos."""
    registro = {
        "legajo": "13220",
        "nombre": "Test",
        "apellido": "User"
    }
    
    id_generado = generar_id(registro)
    
    # Verificar formato: LEGAJO_YYYYMMDD_HHMMSS
    partes = id_generado.split("_")
    assert len(partes) == 3, f"ID debe tener 3 partes separadas por guiones bajos, obtenido: {id_generado}"
    assert partes[0] == "13220", f"Primera parte debe ser el legajo, obtenido: {partes[0]}"
    assert len(partes[1]) == 8, f"Fecha debe tener 8 dígitos (YYYYMMDD), obtenido: {partes[1]}"
    assert len(partes[2]) == 6, f"Hora debe tener 6 dígitos (HHMMSS), obtenido: {partes[2]}"
    assert partes[1].isdigit(), "Fecha debe ser numérica"
    assert partes[2].isdigit(), "Hora debe ser numérica"
    
    print(f"✅ ID con guiones bajos generado correctamente: {id_generado}")
    return True


def test_turnos_dinamicos():
    """Test: Turnos cargados dinámicamente desde CSV."""
    turnos = get_turnos_disponibles()
    
    assert isinstance(turnos, list), "Debe retornar una lista"
    assert len(turnos) > 0, "Debe haber al menos un turno"
    
    # Verificar que tiene los 4 turnos esperados
    assert "Mañana" in turnos, "Debe incluir Mañana"
    assert "Tarde" in turnos, "Debe incluir Tarde"
    assert "Noche" in turnos, "Debe incluir Noche"
    assert "Vespertino" in turnos, "Debe incluir Vespertino"
    
    print(f"✅ Turnos disponibles cargados: {turnos}")
    return True


def test_info_completa_con_cupo():
    """Test: get_info_completa retorna cupo."""
    # Usar una materia que sabemos que existe
    info = get_info_completa(
        "Técnica Instrumental y Lectura a Primera Vista 1: Piano",
        "Anabella Russo",
        "18"
    )
    
    assert info is not None, "Debe encontrar la materia"
    assert "cupo" in info, "Debe incluir el campo cupo"
    assert info["cupo"] == 4, "Debe tener cupo 4"
    
    print(f"✅ Info completa incluye cupo: {info.get('cupo')}")
    return True


def test_contar_inscripciones():
    """Test: contar_inscripciones_materia funciona correctamente."""
    # Esto debería funcionar aunque no haya inscripciones
    count = contar_inscripciones_materia(
        "Test Materia",
        "Test Profesor",
        "A"
    )
    
    assert isinstance(count, int), "Debe retornar un entero"
    assert count >= 0, "El conteo no puede ser negativo"
    
    print(f"✅ Conteo de inscripciones funciona: {count}")
    return True


def test_id_con_dni_fallback():
    """Test: ID usa DNI cuando no hay legajo."""
    registro = {
        "dni": "33668285",
        "nombre": "Test",
        "apellido": "User"
    }
    
    id_generado = generar_id(registro)
    partes = id_generado.split("_")
    
    assert partes[0] == "33668285", f"Debe usar DNI como legajo, obtenido: {partes[0]}"
    
    print(f"✅ ID con DNI fallback: {id_generado}")
    return True


def test_id_sin_legajo_ni_dni():
    """Test: ID temporal cuando no hay legajo ni DNI."""
    registro = {
        "nombre": "Test",
        "apellido": "User"
    }
    
    id_generado = generar_id(registro)
    partes = id_generado.split("_")
    
    assert partes[0] == "TEMP", f"Debe usar TEMP cuando no hay legajo ni DNI, obtenido: {partes[0]}"
    
    print(f"✅ ID temporal: {id_generado}")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("TESTS DE MEJORAS DEL FORMULARIO")
    print("=" * 60)
    
    tests = [
        test_id_format_underscore,
        test_turnos_dinamicos,
        test_info_completa_con_cupo,
        test_contar_inscripciones,
        test_id_con_dni_fallback,
        test_id_sin_legajo_ni_dni,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        print(f"\n🔍 Ejecutando: {test_func.__name__}")
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ FALLÓ: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print(f"\n{'=' * 60}")
    print(f"RESULTADOS: {passed} pasados, {failed} fallidos")
    print(f"{'=' * 60}")
    
    sys.exit(0 if failed == 0 else 1)
