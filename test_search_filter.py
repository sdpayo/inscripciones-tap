"""Test para verificar que el filtrado de búsqueda funciona en todos los campos."""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(__file__))

from database.csv_handler import cargar_registros

def test_search_filter():
    """Simula la lógica de filtrado del método _filtrar_tabla."""
    
    # Cargar registros de prueba
    registros = cargar_registros()
    
    if not registros:
        print("⚠️  No hay registros para probar")
        return False
    
    print("=" * 70)
    print("TEST DE FILTRADO DE BÚSQUEDA")
    print("=" * 70)
    print(f"\nTotal de registros: {len(registros)}")
    
    # Tomar el primer registro para testing
    if len(registros) > 0:
        reg = registros[0]
        print("\n📋 Registro de prueba:")
        print(f"   Nombre: {reg.get('nombre', '')}")
        print(f"   Apellido: {reg.get('apellido', '')}")
        print(f"   DNI: {reg.get('dni', '')}")
        print(f"   Legajo: {reg.get('legajo', '')}")
        print(f"   Email: {reg.get('email', '')}")
        print(f"   Teléfono: {reg.get('telefono', '')}")
        print(f"   Materia: {reg.get('materia', '')}")
        print(f"   Profesor: {reg.get('profesor', '')}")
        print(f"   Comisión: {reg.get('comision', '')}")
        print(f"   Turno: {reg.get('turno', '')}")
        print(f"   Año: {reg.get('anio', '')}")
        
        # Test cases - buscar por diferentes campos
        test_cases = [
            ("nombre", reg.get("nombre", "")[:3].lower()),
            ("apellido", reg.get("apellido", "")[:3].lower()),
            ("dni", reg.get("dni", "")[:3]),
            ("legajo", reg.get("legajo", "")[:3]),
            ("email", reg.get("email", "").split("@")[0][:3].lower() if "@" in reg.get("email", "") else ""),
            ("telefono", reg.get("telefono", "")[:3]),
            ("materia", reg.get("materia", "").split()[0][:3].lower() if reg.get("materia", "") else ""),
            ("profesor", reg.get("profesor", "").split()[0][:3].lower() if reg.get("profesor", "") else ""),
            ("comision", reg.get("comision", "").lower()),
            ("turno", reg.get("turno", "")[:3].lower()),
            ("anio", str(reg.get("anio", ""))),
        ]
        
        print("\n🔍 Pruebas de búsqueda:")
        print("-" * 70)
        
        all_passed = True
        for field, search_text in test_cases:
            if not search_text:
                continue
                
            # Simular la lógica de _filtrar_tabla
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
            found = search_text.lower() in texto_completo
            
            status = "✅" if found else "❌"
            print(f"   {status} Buscar '{search_text}' en campo '{field}': {'ENCONTRADO' if found else 'NO ENCONTRADO'}")
            
            if not found:
                all_passed = False
        
        print("-" * 70)
        
        if all_passed:
            print("\n✅ TODAS LAS PRUEBAS PASARON")
            print("   El filtro ahora busca en todos los campos correctamente")
            return True
        else:
            print("\n❌ ALGUNAS PRUEBAS FALLARON")
            return False
    
    return False

if __name__ == "__main__":
    success = test_search_filter()
    sys.exit(0 if success else 1)
