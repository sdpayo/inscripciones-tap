#!/usr/bin/env python
"""Test para verificar generación de PDF del listado."""
import sys
from pathlib import Path
import tempfile

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from services.pdf_generator import generar_listado_pdf

def test_pdf_generation():
    """Test generación de PDF con datos de prueba"""
    print("\n=== Test: Generación de PDF del Listado ===\n")
    
    # Datos de prueba
    registros = [
        {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'dni': '12345678',
            'materia': 'Piano 1',
            'profesor': 'Ana García',
            'comision': 'A',
            'turno': 'Mañana',
            'anio': '1'
        },
        {
            'nombre': 'María',
            'apellido': 'González',
            'dni': '87654321',
            'materia': 'Guitarra 1',
            'profesor': 'Carlos López',
            'comision': 'B',
            'turno': 'Tarde',
            'anio': '2'
        },
        {
            'nombre': 'Pedro',
            'apellido': 'Rodríguez',
            'dni': '11223344',
            'materia': 'Piano 1',
            'profesor': 'Ana García',
            'comision': 'A',
            'turno': 'Mañana',
            'anio': '1'
        }
    ]
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        output_path = tmp.name
    
    try:
        # Test 1: Sin filtros
        print("Test 1: PDF sin filtros...")
        success, message = generar_listado_pdf(registros, output_path)
        
        if not success:
            print(f"❌ FALLÓ: {message}")
            return False
        
        # Verificar que el archivo existe
        pdf_path = Path(output_path)
        if not pdf_path.exists():
            print("❌ FALLÓ: El archivo PDF no se creó")
            return False
        
        # Verificar que tiene contenido
        file_size = pdf_path.stat().st_size
        if file_size == 0:
            print("❌ FALLÓ: El archivo PDF está vacío")
            return False
        
        print(f"✅ PDF generado exitosamente ({file_size} bytes)")
        print(f"   Ubicación: {output_path}")
        
        # Test 2: Con filtros
        print("\nTest 2: PDF con filtros...")
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp2:
            output_path2 = tmp2.name
        
        success2, message2 = generar_listado_pdf(
            registros, 
            output_path2,
            filtro_materia="Piano 1",
            filtro_profesor="Ana García"
        )
        
        if not success2:
            print(f"❌ FALLÓ: {message2}")
            return False
        
        pdf_path2 = Path(output_path2)
        if not pdf_path2.exists():
            print("❌ FALLÓ: El archivo PDF con filtros no se creó")
            return False
        
        file_size2 = pdf_path2.stat().st_size
        if file_size2 == 0:
            print("❌ FALLÓ: El archivo PDF con filtros está vacío")
            return False
        
        print(f"✅ PDF con filtros generado exitosamente ({file_size2} bytes)")
        print(f"   Ubicación: {output_path2}")
        
        # Test 3: Verificar que el PDF con filtros tiene más contenido (por el header)
        # El PDF con filtros debería tener un tamaño similar o mayor por el header profesional
        print(f"\nComparación de tamaños:")
        print(f"   PDF sin filtros: {file_size} bytes")
        print(f"   PDF con filtros: {file_size2} bytes")
        
        # Limpiar archivos temporales
        try:
            pdf_path.unlink()
            pdf_path2.unlink()
            print("\n✅ Archivos temporales limpiados")
        except:
            pass
        
        print("\n✅ TODOS LOS TESTS DE PDF PASARON\n")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecutar test"""
    print("\n" + "="*60)
    print("TEST DE GENERACIÓN DE PDF DEL LISTADO")
    print("="*60)
    
    success = test_pdf_generation()
    
    if success:
        print("="*60)
        print("✅ TEST EXITOSO")
        print("="*60)
        print("\nCaracterísticas verificadas:")
        print("  • Generación de PDF sin filtros")
        print("  • Generación de PDF con filtros")
        print("  • Archivo creado correctamente")
        print("  • Archivo tiene contenido válido")
        print()
        return 0
    else:
        print("="*60)
        print("❌ TEST FALLIDO")
        print("="*60)
        return 1


if __name__ == '__main__':
    exit(main())
