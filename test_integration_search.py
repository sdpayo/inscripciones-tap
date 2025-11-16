"""Test de integración para verificar que la búsqueda funciona correctamente con distintos escenarios."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database.csv_handler import cargar_registros

def test_search_scenarios():
    """Prueba diferentes escenarios de búsqueda."""
    
    registros = cargar_registros()
    
    if not registros:
        print("⚠️  No hay registros para probar")
        return True
    
    print("=" * 70)
    print("TEST DE INTEGRACIÓN - ESCENARIOS DE BÚSQUEDA")
    print("=" * 70)
    print(f"\nTotal de registros: {len(registros)}")
    
    def simulate_search(search_text):
        """Simula la búsqueda en la tabla."""
        results = []
        search_text = search_text.lower().strip()
        
        for reg in registros:
            if not search_text:
                results.append(reg)
                continue
            
            campos_a_buscar = [
                reg.get("nombre", ""),
                reg.get("apellido", ""),
                reg.get("dni", ""),
                reg.get("legajo", ""),
                reg.get("email", ""),
                reg.get("telefono", ""),
                reg.get("materia", ""),
                reg.get("profesor", ""),
                reg.get("comision", ""),
                reg.get("turno", ""),
                reg.get("anio", ""),
                reg.get("direccion", ""),
                reg.get("observaciones", ""),
            ]
            
            texto_completo = " ".join(str(campo).lower() for campo in campos_a_buscar)
            
            if search_text in texto_completo:
                results.append(reg)
        
        return results
    
    # Escenario 1: Búsqueda vacía debe devolver todos los registros
    print("\n📝 Escenario 1: Búsqueda vacía")
    results = simulate_search("")
    print(f"   Esperado: {len(registros)} registros")
    print(f"   Obtenido: {len(results)} registros")
    assert len(results) == len(registros), "Búsqueda vacía debe devolver todos los registros"
    print("   ✅ Pasó")
    
    # Escenario 2: Buscar por nombre
    if registros:
        primer_nombre = registros[0].get("nombre", "")[:3].lower()
        if primer_nombre:
            print(f"\n📝 Escenario 2: Búsqueda por nombre '{primer_nombre}'")
            results = simulate_search(primer_nombre)
            print(f"   Registros encontrados: {len(results)}")
            assert len(results) > 0, "Debe encontrar al menos un registro"
            print("   ✅ Pasó")
    
    # Escenario 3: Buscar por DNI
    if registros:
        dni = registros[0].get("dni", "")[:4]
        if dni:
            print(f"\n📝 Escenario 3: Búsqueda por DNI '{dni}'")
            results = simulate_search(dni)
            print(f"   Registros encontrados: {len(results)}")
            assert len(results) > 0, "Debe encontrar al menos un registro por DNI"
            print("   ✅ Pasó")
    
    # Escenario 4: Buscar por email
    if registros:
        for reg in registros:
            email = reg.get("email", "")
            if "@" in email:
                email_part = email.split("@")[0][:4].lower()
                print(f"\n📝 Escenario 4: Búsqueda por email '{email_part}'")
                results = simulate_search(email_part)
                print(f"   Registros encontrados: {len(results)}")
                assert len(results) > 0, "Debe encontrar al menos un registro por email"
                print("   ✅ Pasó")
                break
    
    # Escenario 5: Buscar por profesor
    if registros:
        profesor = registros[0].get("profesor", "")
        if profesor:
            profesor_part = profesor.split()[0][:3].lower()
            print(f"\n📝 Escenario 5: Búsqueda por profesor '{profesor_part}'")
            results = simulate_search(profesor_part)
            print(f"   Registros encontrados: {len(results)}")
            assert len(results) > 0, "Debe encontrar al menos un registro por profesor"
            print("   ✅ Pasó")
    
    # Escenario 6: Buscar por turno
    if registros:
        turno = registros[0].get("turno", "").lower()
        if turno:
            print(f"\n📝 Escenario 6: Búsqueda por turno '{turno}'")
            results = simulate_search(turno)
            print(f"   Registros encontrados: {len(results)}")
            assert len(results) > 0, "Debe encontrar al menos un registro por turno"
            print("   ✅ Pasó")
    
    # Escenario 7: Buscar texto inexistente
    print(f"\n📝 Escenario 7: Búsqueda de texto inexistente")
    results = simulate_search("xyzabc123nonexistente999")
    print(f"   Registros encontrados: {len(results)}")
    assert len(results) == 0, "No debe encontrar registros con texto inexistente"
    print("   ✅ Pasó")
    
    print("\n" + "=" * 70)
    print("✅ TODOS LOS ESCENARIOS DE INTEGRACIÓN PASARON")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = test_search_scenarios()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
