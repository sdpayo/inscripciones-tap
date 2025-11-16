"""Test nuevo sistema de generación de IDs con formato legajo-fecha-hora."""
import sys
from datetime import datetime
from database.csv_handler import generar_id, migrar_id_si_es_uuid


def test_generar_id_con_legajo():
    """Test: Generar ID con legajo."""
    registro = {
        "legajo": "13220",
        "nombre": "Damian",
        "apellido": "Payo"
    }
    
    id_generado = generar_id(registro)
    
    # Verificar formato: LEGAJO-YYYYMMDD-HHMM
    partes = id_generado.split("-")
    assert len(partes) == 3, f"ID debe tener 3 partes separadas por guiones, obtenido: {id_generado}"
    assert partes[0] == "13220", f"Primera parte debe ser el legajo, obtenido: {partes[0]}"
    assert len(partes[1]) == 8, f"Fecha debe tener 8 dígitos (YYYYMMDD), obtenido: {partes[1]}"
    assert len(partes[2]) == 4, f"Hora debe tener 4 dígitos (HHMM), obtenido: {partes[2]}"
    assert partes[1].isdigit(), "Fecha debe ser numérica"
    assert partes[2].isdigit(), "Hora debe ser numérica"
    
    print(f"✅ ID con legajo generado correctamente: {id_generado}")
    return True


def test_generar_id_con_dni_fallback():
    """Test: Generar ID usando DNI cuando no hay legajo."""
    registro = {
        "dni": "33668285",
        "nombre": "Juan",
        "apellido": "Pérez"
    }
    
    id_generado = generar_id(registro)
    
    # Verificar que usa DNI como legajo
    partes = id_generado.split("-")
    assert partes[0] == "33668285", f"Debe usar DNI cuando no hay legajo, obtenido: {partes[0]}"
    
    print(f"✅ ID con DNI fallback generado correctamente: {id_generado}")
    return True


def test_generar_id_sin_datos():
    """Test: Generar ID cuando no hay ni legajo ni DNI."""
    registro = {
        "nombre": "Test",
        "apellido": "Usuario"
    }
    
    id_generado = generar_id(registro)
    
    # Verificar que usa TEMP
    partes = id_generado.split("-")
    assert partes[0] == "TEMP", f"Debe usar TEMP cuando no hay legajo ni DNI, obtenido: {partes[0]}"
    
    print(f"✅ ID TEMP generado correctamente: {id_generado}")
    return True


def test_generar_id_sin_registro():
    """Test: Generar ID cuando no se pasa registro."""
    id_generado = generar_id()
    
    # Verificar que funciona sin parámetros
    partes = id_generado.split("-")
    assert partes[0] == "TEMP", "Debe usar TEMP cuando no hay registro"
    
    print(f"✅ ID sin registro generado correctamente: {id_generado}")
    return True


def test_migrar_uuid_a_nuevo_formato():
    """Test: Migrar ID antiguo UUID a nuevo formato."""
    registro = {
        "id": "deaa95af-a3ec-4b4a-b075-f70e80bcfe0c",
        "legajo": "13220",
        "nombre": "Damian",
        "apellido": "Payo"
    }
    
    registro_migrado = migrar_id_si_es_uuid(registro)
    
    # Verificar que el ID fue migrado
    nuevo_id = registro_migrado.get("id")
    assert nuevo_id != "deaa95af-a3ec-4b4a-b075-f70e80bcfe0c", "ID debe haber cambiado"
    assert "13220" in nuevo_id, f"Nuevo ID debe contener el legajo, obtenido: {nuevo_id}"
    assert nuevo_id.count("-") == 2, f"Nuevo ID debe tener formato LEGAJO-FECHA-HORA, obtenido: {nuevo_id}"
    
    print(f"✅ ID UUID migrado correctamente: deaa95af... -> {nuevo_id}")
    return True


def test_no_migrar_id_nuevo_formato():
    """Test: No migrar ID que ya está en nuevo formato."""
    registro = {
        "id": "13220-20251116-2129",
        "legajo": "13220",
        "nombre": "Damian"
    }
    
    registro_migrado = migrar_id_si_es_uuid(registro)
    
    # Verificar que el ID no cambió
    assert registro_migrado.get("id") == "13220-20251116-2129", "ID en nuevo formato no debe cambiar"
    
    print(f"✅ ID en nuevo formato no fue modificado: {registro_migrado.get('id')}")
    return True


def test_formato_fecha_hora_correcto():
    """Test: Verificar que fecha y hora son válidas."""
    registro = {"legajo": "12345"}
    id_generado = generar_id(registro)
    partes = id_generado.split("-")
    
    # Verificar que la fecha es válida
    fecha_str = partes[1]
    try:
        datetime.strptime(fecha_str, "%Y%m%d")
        print(f"✅ Fecha válida: {fecha_str}")
    except ValueError:
        raise AssertionError(f"Fecha inválida: {fecha_str}")
    
    # Verificar que la hora es válida
    hora_str = partes[2]
    try:
        datetime.strptime(hora_str, "%H%M")
        print(f"✅ Hora válida: {hora_str}")
    except ValueError:
        raise AssertionError(f"Hora inválida: {hora_str}")
    
    return True


def test_limpieza_caracteres_especiales():
    """Test: Verificar que se limpian caracteres especiales del legajo."""
    registro = {
        "legajo": "ABC-123/456",  # Contiene guiones y barras
        "nombre": "Test"
    }
    
    id_generado = generar_id(registro)
    partes = id_generado.split("-")
    
    # Verificar que solo quedan alfanuméricos
    assert partes[0] == "ABC123456", f"Legajo debe contener solo alfanuméricos, obtenido: {partes[0]}"
    
    print(f"✅ Caracteres especiales eliminados correctamente: {partes[0]}")
    return True


# Ejecutar todos los tests
if __name__ == "__main__":
    tests = [
        test_generar_id_con_legajo,
        test_generar_id_con_dni_fallback,
        test_generar_id_sin_datos,
        test_generar_id_sin_registro,
        test_migrar_uuid_a_nuevo_formato,
        test_no_migrar_id_nuevo_formato,
        test_formato_fecha_hora_correcto,
        test_limpieza_caracteres_especiales
    ]
    
    print("=" * 60)
    print("TESTS DE SISTEMA DE IDs MEJORADO")
    print("=" * 60)
    
    exitosos = 0
    fallidos = 0
    
    for test in tests:
        try:
            print(f"\n🔍 Ejecutando: {test.__name__}")
            if test():
                exitosos += 1
        except AssertionError as e:
            print(f"❌ FALLÓ: {e}")
            fallidos += 1
        except Exception as e:
            print(f"❌ ERROR INESPERADO: {e}")
            fallidos += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTADO: {exitosos} exitosos, {fallidos} fallidos")
    print("=" * 60)
    
    if fallidos > 0:
        sys.exit(1)
    else:
        print("\n🎉 ¡Todos los tests pasaron exitosamente!")
        sys.exit(0)
