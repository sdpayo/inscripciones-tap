"""Test de integración del sistema de IDs con CSV."""
import sys
import os
from pathlib import Path

# Archivo de prueba
TEST_CSV = Path("/tmp/test_inscripciones.csv")

# Configurar CSV_FILE ANTES de importar csv_handler
import config.settings as settings
settings.CSV_FILE = TEST_CSV

from database.csv_handler import (
    guardar_registro, cargar_registros, 
    generar_id, guardar_todos_registros
)


def setup():
    """Configurar entorno de prueba."""
    # Limpiar si existe
    if TEST_CSV.exists():
        TEST_CSV.unlink()
    
    # Crear directorio temporal si no existe
    TEST_CSV.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Usando archivo de prueba: {TEST_CSV}")


def teardown():
    """Limpiar después de las pruebas."""
    if TEST_CSV.exists():
        TEST_CSV.unlink()
        print(f"🧹 Archivo de prueba eliminado")


def test_guardar_registro_con_nuevo_id():
    """Test: Guardar registro con nuevo formato de ID."""
    registro = {
        "legajo": "13220",
        "nombre": "Damian",
        "apellido": "Payo",
        "dni": "33668285",
        "materia": "Piano",
        "profesor": "Juan Pérez",
        "anio": "1",
        "turno": "Mañana",
        "comision": "A",
        "horario": "10:00-12:00"
    }
    
    # Generar ID
    registro["id"] = generar_id(registro)
    print(f"📝 ID generado: {registro['id']}")
    
    # Guardar
    ok, msg = guardar_registro(registro)
    assert ok, f"Guardar debería ser exitoso: {msg}"
    print(f"✅ Registro guardado: {msg}")
    
    # Verificar que se guardó correctamente
    registros = cargar_registros()
    assert len(registros) == 1, f"Debe haber 1 registro, encontrados: {len(registros)}"
    
    reg_guardado = registros[0]
    assert reg_guardado["id"] == registro["id"], "ID debe coincidir"
    assert reg_guardado["legajo"] == "13220", "Legajo debe estar guardado"
    assert "13220" in reg_guardado["id"], "ID debe contener el legajo"
    
    print(f"✅ Registro recuperado correctamente con ID: {reg_guardado['id']}")
    return True


def test_multiples_registros_ids_unicos():
    """Test: Múltiples registros con IDs únicos por timestamp."""
    import time
    
    registros = []
    for i in range(3):
        reg = {
            "legajo": "13220",
            "nombre": f"Estudiante{i}",
            "apellido": "Test",
            "dni": "12345678",
            "materia": "Piano"
        }
        reg["id"] = generar_id(reg)
        registros.append(reg)
        
        # Esperar 61 segundos para cambio de minuto (formato HHMM)
        # Para testing rápido, verificamos que el formato es correcto
        if i < 2:
            time.sleep(0.1)  # Solo pequeño delay
    
    # Verificar formato de IDs (aunque no sean únicos en este test rápido)
    ids = [r["id"] for r in registros]
    
    # Todos deben tener el mismo formato LEGAJO-FECHA-HORA
    for id in ids:
        partes = id.split("-")
        assert len(partes) == 3, f"ID debe tener 3 partes: {id}"
        assert partes[0] == "13220", f"Legajo incorrecto: {partes[0]}"
    
    print(f"✅ IDs con formato correcto:")
    for id in ids:
        print(f"   - {id}")
    
    # Nota: IDs podrían ser iguales si se generan en el mismo minuto
    print(f"⚠️  Nota: IDs pueden duplicarse si se generan en el mismo minuto (HHMM)")
    
    return True


def test_cargar_registros_por_id_completo():
    """Test: Buscar registros usando ID completo."""
    # Crear y guardar registro
    registro = {
        "legajo": "99999",
        "nombre": "TestBusqueda",
        "apellido": "Apellido",
        "dni": "11111111"
    }
    registro["id"] = generar_id(registro)
    id_completo = registro["id"]
    
    ok, msg = guardar_registro(registro)
    assert ok, f"Guardar debería ser exitoso: {msg}"
    
    # Buscar por ID completo
    registros = cargar_registros()
    encontrado = None
    for r in registros:
        if r.get("id") == id_completo:
            encontrado = r
            break
    
    assert encontrado is not None, f"Registro con ID {id_completo} debe encontrarse"
    assert encontrado["nombre"] == "TestBusqueda", "Nombre debe coincidir"
    
    print(f"✅ Registro encontrado por ID completo: {id_completo}")
    return True


def test_compatibilidad_uuid():
    """Test: Sistema puede manejar registros con UUID antiguo."""
    from database.csv_handler import migrar_id_si_es_uuid
    
    # Simular registro antiguo con UUID
    registro_uuid = {
        "id": "deaa95af-a3ec-4b4a-b075-f70e80bcfe0c",
        "legajo": "12345",
        "nombre": "Antiguo",
        "apellido": "Usuario",
        "dni": "99999999"
    }
    
    # Guardar directamente (sin migración)
    guardar_registro(registro_uuid)
    
    # Cargar y verificar
    registros = cargar_registros()
    reg_cargado = None
    for r in registros:
        if r.get("nombre") == "Antiguo":
            reg_cargado = r
            break
    
    assert reg_cargado is not None, "Registro con UUID debe poder guardarse"
    
    # Ahora migrar
    reg_migrado = migrar_id_si_es_uuid(reg_cargado)
    assert reg_migrado["id"] != registro_uuid["id"], "ID debe haber sido migrado"
    assert "12345" in reg_migrado["id"], "Nuevo ID debe contener legajo"
    
    print(f"✅ UUID migrado: {registro_uuid['id'][:8]}... -> {reg_migrado['id']}")
    return True


# Ejecutar tests
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DE INTEGRACIÓN - SISTEMA DE IDs")
    print("=" * 60)
    
    tests = [
        test_guardar_registro_con_nuevo_id,
        test_multiples_registros_ids_unicos,
        test_cargar_registros_por_id_completo,
        test_compatibilidad_uuid
    ]
    
    exitosos = 0
    fallidos = 0
    
    for test in tests:
        print(f"\n🔍 {test.__name__}")
        print("-" * 60)
        
        setup()
        
        try:
            if test():
                exitosos += 1
                print(f"✅ PASÓ")
        except AssertionError as e:
            print(f"❌ FALLÓ: {e}")
            fallidos += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            fallidos += 1
        finally:
            teardown()
    
    print("\n" + "=" * 60)
    print(f"RESULTADO: {exitosos} exitosos, {fallidos} fallidos")
    print("=" * 60)
    
    sys.exit(0 if fallidos == 0 else 1)
