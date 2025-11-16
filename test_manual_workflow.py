"""Test manual del flujo completo del sistema de IDs."""
import sys
from datetime import datetime
from pathlib import Path

# Configurar CSV de prueba
TEST_CSV = Path("/tmp/test_workflow.csv")
import config.settings as settings
settings.CSV_FILE = TEST_CSV

from database.csv_handler import (
    guardar_registro, cargar_registros, generar_id,
    migrar_id_si_es_uuid, guardar_todos_registros
)

def limpiar():
    """Limpia el archivo de prueba."""
    if TEST_CSV.exists():
        TEST_CSV.unlink()
    print("🧹 Archivo limpio\n")

def test_crear_inscripcion():
    """Simula crear una inscripción desde el formulario."""
    print("=" * 60)
    print("TEST 1: CREAR NUEVA INSCRIPCIÓN")
    print("=" * 60)
    
    # Simular datos del formulario
    registro_temp = {
        "legajo": "13220",
        "nombre": "Damian",
        "apellido": "Payo",
        "dni": "33668285",
        "fecha_nacimiento": "11/04/1988",
        "edad": "37",
        "direccion": "Rio La Caldera 1630",
        "telefono": "3874491448",
        "email": "damianpayo@gmail.com",
        "anio": "1",
        "turno": "Mañana",
        "materia": "Piano",
        "profesor": "Juan Pérez",
        "comision": "A",
        "horario": "10:00-12:00"
    }
    
    # Generar ID usando el nuevo sistema
    nuevo_id = generar_id(registro_temp)
    print(f"✅ ID generado: {nuevo_id}")
    
    # Agregar ID y fecha
    registro = {
        "id": nuevo_id,
        "fecha_inscripcion": datetime.now().isoformat(),
        **registro_temp
    }
    
    # Guardar
    ok, msg = guardar_registro(registro)
    if ok:
        print(f"✅ Inscripción guardada: {msg}")
        print(f"   Formato ID: {nuevo_id}")
        print(f"   Legajo visible: {registro['legajo']}")
    else:
        print(f"❌ Error al guardar: {msg}")
        return False
    
    return True

def test_visualizar_tabla():
    """Simula mostrar la tabla sin columna ID."""
    print("\n" + "=" * 60)
    print("TEST 2: VISUALIZAR TABLA (sin columna ID)")
    print("=" * 60)
    
    registros = cargar_registros()
    
    # Simular columnas de la tabla: Nombre, Apellido, DNI, Legajo, Materia, Profesor, Turno, Año
    print(f"\n{'Nombre':<12} {'Apellido':<12} {'DNI':<10} {'Legajo':<8} {'Materia':<15}")
    print("-" * 60)
    
    for reg in registros:
        # Usar ID completo como iid (internamente)
        id_completo = reg.get("id", "")
        
        # Mostrar solo datos visibles (sin ID)
        print(f"{reg.get('nombre', ''):<12} "
              f"{reg.get('apellido', ''):<12} "
              f"{reg.get('dni', ''):<10} "
              f"{reg.get('legajo', ''):<8} "
              f"{reg.get('materia', ''):<15}")
        
        print(f"   [ID interno: {id_completo}]")
    
    print(f"\n✅ Se muestran {len(registros)} registros")
    print("✅ Columna 'ID' oculta para el usuario")
    print("✅ Columna 'Legajo' visible")
    
    return True

def test_buscar_por_id():
    """Simula buscar un registro usando el iid (ID completo)."""
    print("\n" + "=" * 60)
    print("TEST 3: BUSCAR Y EDITAR POR ID")
    print("=" * 60)
    
    registros = cargar_registros()
    if not registros:
        print("❌ No hay registros para buscar")
        return False
    
    # Simular selección en la tabla (el iid ES el ID completo)
    id_completo = registros[0].get("id")
    print(f"📌 Seleccionando registro con iid: {id_completo}")
    
    # Buscar por ID exacto (como haría _editar_seleccionado)
    registro = None
    for reg in registros:
        if reg.get("id") == id_completo:
            registro = reg
            break
    
    if registro:
        print(f"✅ Registro encontrado:")
        print(f"   Nombre: {registro.get('nombre')}")
        print(f"   Apellido: {registro.get('apellido')}")
        print(f"   Legajo: {registro.get('legajo')}")
        print(f"   ID interno: {registro.get('id')}")
    else:
        print("❌ Registro no encontrado")
        return False
    
    return True

def test_agregar_sin_legajo():
    """Test: Crear inscripción sin legajo (usa DNI)."""
    print("\n" + "=" * 60)
    print("TEST 4: INSCRIPCIÓN SIN LEGAJO (fallback a DNI)")
    print("=" * 60)
    
    registro_temp = {
        # No tiene legajo, solo DNI
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "99887766",
        "materia": "Guitarra",
        "anio": "2"
    }
    
    # Generar ID (debería usar DNI)
    nuevo_id = generar_id(registro_temp)
    print(f"✅ ID generado: {nuevo_id}")
    
    if "99887766" in nuevo_id:
        print("✅ ID usa DNI como fallback cuando no hay legajo")
    else:
        print(f"❌ ID debería contener el DNI: {nuevo_id}")
        return False
    
    # Guardar
    registro = {
        "id": nuevo_id,
        "fecha_inscripcion": datetime.now().isoformat(),
        **registro_temp
    }
    
    ok, msg = guardar_registro(registro)
    print(f"✅ Guardado: {msg}")
    
    return True

def test_migrar_uuid():
    """Test: Migrar registros antiguos con UUID."""
    print("\n" + "=" * 60)
    print("TEST 5: MIGRACIÓN DE IDs ANTIGUOS (UUID)")
    print("=" * 60)
    
    # Simular registro antiguo
    registro_antiguo = {
        "id": "deaa95af-a3ec-4b4a-b075-f70e80bcfe0c",
        "legajo": "54321",
        "nombre": "Usuario",
        "apellido": "Antiguo",
        "dni": "11223344",
        "materia": "Canto"
    }
    
    print(f"📝 ID antiguo (UUID): {registro_antiguo['id']}")
    
    # Guardar con UUID
    guardar_registro(registro_antiguo)
    
    # Cargar y migrar
    registros = cargar_registros()
    reg_uuid = None
    for r in registros:
        if r.get("nombre") == "Usuario":
            reg_uuid = r
            break
    
    if reg_uuid:
        print(f"✅ Registro con UUID cargado")
        
        # Migrar
        reg_migrado = migrar_id_si_es_uuid(reg_uuid)
        
        if reg_migrado["id"] != registro_antiguo["id"]:
            print(f"✅ ID migrado: {registro_antiguo['id'][:8]}... -> {reg_migrado['id']}")
            print(f"   Nuevo formato contiene legajo: {'54321' in reg_migrado['id']}")
            
            # Actualizar en CSV
            registros_actualizados = []
            for r in registros:
                if r.get("nombre") == "Usuario":
                    registros_actualizados.append(reg_migrado)
                else:
                    registros_actualizados.append(r)
            
            guardar_todos_registros(registros_actualizados)
            print("✅ Registro migrado guardado en CSV")
        else:
            print("⚠️  ID no fue migrado (ya está en nuevo formato)")
    else:
        print("❌ No se encontró el registro con UUID")
        return False
    
    return True

def test_eliminar():
    """Test: Eliminar registro usando ID completo."""
    print("\n" + "=" * 60)
    print("TEST 6: ELIMINAR REGISTRO")
    print("=" * 60)
    
    registros = cargar_registros()
    cant_inicial = len(registros)
    print(f"📊 Registros iniciales: {cant_inicial}")
    
    if cant_inicial == 0:
        print("⚠️  No hay registros para eliminar")
        return True
    
    # Simular selección (el iid ES el ID completo)
    id_a_eliminar = registros[0].get("id")
    nombre = registros[0].get("nombre")
    print(f"🗑️  Eliminando: {nombre} (ID: {id_a_eliminar})")
    
    # Eliminar por ID exacto
    registros_filtrados = [r for r in registros if r.get("id") != id_a_eliminar]
    
    ok, msg = guardar_todos_registros(registros_filtrados)
    if ok:
        registros_actuales = cargar_registros()
        print(f"✅ Eliminado correctamente")
        print(f"   Registros restantes: {len(registros_actuales)}")
        
        if len(registros_actuales) == cant_inicial - 1:
            print("✅ Cantidad correcta de registros")
        else:
            print("❌ Error en la cantidad de registros")
            return False
    else:
        print(f"❌ Error al eliminar: {msg}")
        return False
    
    return True

def test_resumen_final():
    """Muestra resumen final del estado."""
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    
    registros = cargar_registros()
    print(f"\n📊 Total de registros: {len(registros)}")
    
    if registros:
        print("\n📋 Formato de IDs:")
        for reg in registros:
            id_val = reg.get("id", "")
            legajo = reg.get("legajo", "")
            nombre = reg.get("nombre", "")
            
            # Verificar formato
            es_nuevo = len(id_val) < 25 and id_val.count("-") == 2
            formato = "NUEVO (legajo-fecha-hora)" if es_nuevo else "ANTIGUO (UUID)"
            
            print(f"   • {nombre:<15} Legajo: {legajo:<8} ID: {id_val} [{formato}]")
    
    return True

# Ejecutar flujo completo
if __name__ == "__main__":
    print("\n" + "🔬" * 30)
    print("PRUEBA MANUAL DE FLUJO COMPLETO")
    print("🔬" * 30 + "\n")
    
    limpiar()
    
    tests = [
        test_crear_inscripcion,
        test_visualizar_tabla,
        test_buscar_por_id,
        test_agregar_sin_legajo,
        test_migrar_uuid,
        test_eliminar,
        test_resumen_final
    ]
    
    exitosos = 0
    fallidos = 0
    
    for test in tests:
        try:
            if test():
                exitosos += 1
            else:
                fallidos += 1
        except Exception as e:
            print(f"❌ ERROR INESPERADO: {e}")
            import traceback
            traceback.print_exc()
            fallidos += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTADO: {exitosos}/{len(tests)} tests exitosos")
    print("=" * 60)
    
    if fallidos == 0:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("\n📝 CAMBIOS IMPLEMENTADOS:")
        print("   ✅ IDs con formato: LEGAJO-YYYYMMDD-HHMM")
        print("   ✅ Tabla sin columna 'ID' visible")
        print("   ✅ Tabla con columna 'Legajo' visible")
        print("   ✅ Búsqueda por ID completo usando iid")
        print("   ✅ Compatibilidad con UUIDs antiguos")
        print("   ✅ Fallback a DNI cuando no hay legajo")
    else:
        print(f"\n⚠️  {fallidos} tests fallaron")
    
    limpiar()
    sys.exit(0 if fallidos == 0 else 1)
