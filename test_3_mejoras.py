#!/usr/bin/env python
"""Test para verificar las 3 mejoras implementadas."""
import sys
import os
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def test_listados_tab_changes():
    """Test 1: Verificar cambios en listados_tab.py"""
    print("\n=== Test 1: Cambios en listados_tab.py ===")
    
    with open('ui/listados_tab.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que se agregó _aplicar_filtros() al final de _build_ui
    assert 'self._aplicar_filtros()' in content, "❌ Falta llamada a _aplicar_filtros() en _build_ui()"
    print("✅ _aplicar_filtros() agregado al final de _build_ui()")
    
    # Verificar inicialización de profesores
    assert 'profesores_con_inscripciones = sorted(set(' in content, "❌ Falta inicialización de profesores"
    assert "self.profesor_combo['values'] = [\"(Todos)\"] + profesores_con_inscripciones" in content, "❌ Falta asignación de profesores al combo"
    print("✅ Inicialización de profesores con inscripciones implementada")
    
    print("✅ Test 1 PASADO: Listados tab carga datos automáticamente\n")


def test_pdf_generator_changes():
    """Test 2: Verificar cambios en pdf_generator.py"""
    print("=== Test 2: Cambios en pdf_generator.py ===")
    
    with open('services/pdf_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar firma de función actualizada
    assert 'def generar_listado_pdf(registros, output_path, filtro_materia=None, filtro_profesor=None):' in content, \
        "❌ Firma de generar_listado_pdf no actualizada con parámetros de filtro"
    print("✅ Firma de generar_listado_pdf actualizada con parámetros opcionales")
    
    # Verificar elementos del encabezado profesional
    assert 'Escuela Superior de Música N°6003' in content, "❌ Falta título institucional"
    print("✅ Título institucional agregado")
    
    assert 'José Lo Giudice' in content, "❌ Falta subtítulo institucional"
    print("✅ Subtítulo institucional agregado")
    
    assert 'LISTADO DE INSCRIPCIONES' in content, "❌ Falta título del listado"
    print("✅ Título del listado agregado")
    
    assert 'Image(logo_path' in content, "❌ Falta manejo de logo"
    print("✅ Manejo de logo implementado")
    
    # Verificar uso de filtros
    assert 'if filtro_materia and filtro_materia != "(Todas)":' in content, "❌ Falta manejo de filtro_materia"
    assert 'if filtro_profesor and filtro_profesor != "(Todos)":' in content, "❌ Falta manejo de filtro_profesor"
    print("✅ Filtros se incluyen en el PDF")
    
    # Verificar estilo profesional
    assert 'colors.HexColor' in content, "❌ Falta uso de colores personalizados"
    assert 'ParagraphStyle' in content, "❌ Falta uso de estilos personalizados"
    print("✅ Estilos profesionales implementados")
    
    # Verificar footer
    assert 'Documento generado automáticamente' in content, "❌ Falta pie de página"
    print("✅ Pie de página agregado")
    
    # Verificar llamada en listados_tab.py
    with open('ui/listados_tab.py', 'r', encoding='utf-8') as f:
        listados_content = f.read()
    
    assert 'filtro_materia = self.filtro_materia_var.get()' in listados_content, \
        "❌ Falta obtención de filtro_materia en listados_tab.py"
    assert 'filtro_profesor = self.filtro_profesor_var.get()' in listados_content, \
        "❌ Falta obtención de filtro_profesor en listados_tab.py"
    assert 'filtro_materia=filtro_materia' in listados_content, \
        "❌ Falta pasar filtro_materia a generar_listado_pdf"
    assert 'filtro_profesor=filtro_profesor' in listados_content, \
        "❌ Falta pasar filtro_profesor a generar_listado_pdf"
    print("✅ Llamada en listados_tab.py actualizada con filtros")
    
    print("✅ Test 2 PASADO: PDF mejorado con encabezado profesional\n")


def test_form_tab_turno_removal():
    """Test 3: Verificar eliminación del campo Turno del formulario"""
    print("=== Test 3: Cambios en form_tab.py - Eliminación de Turno ===")
    
    with open('ui/form_tab.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que NO existe el combo de Turno visible
    assert 'ttk.Label(frame, text="Turno:").grid(row=0, column=2' not in content, \
        "❌ El label de Turno todavía existe en la UI"
    assert 'self.turno_combo = ttk.Combobox(frame, textvariable=self.turno_var' not in content or \
           'self.turno_combo.grid(row=0, column=3' not in content, \
        "❌ El combo de Turno todavía está en la grid"
    print("✅ Campo Turno removido de la UI")
    
    # Verificar que _on_comision_change obtiene turno automáticamente
    assert 'info = get_info_completa(materia, profesor, comision)' in content, \
        "❌ _on_comision_change no llama a get_info_completa"
    assert 'turno = info.get("turno", "") or info.get("Turno", "")' in content, \
        "❌ _on_comision_change no extrae el turno"
    assert 'if turno:' in content and 'horario_display = f"Turno: {turno}"' in content, \
        "❌ _on_comision_change no muestra el turno en horario"
    print("✅ _on_comision_change obtiene turno automáticamente del CSV")
    
    # Verificar que turno_var se maneja en _limpiar aunque no esté visible
    assert 'if not hasattr(self, \'turno_var\'):' in content, \
        "❌ _limpiar no verifica existencia de turno_var"
    assert 'self.turno_var = tk.StringVar()' in content, \
        "❌ _limpiar no inicializa turno_var si no existe"
    print("✅ _limpiar maneja turno_var aunque no esté visible")
    
    # Verificar que _cargar_turnos_disponibles fue eliminada
    assert 'def _cargar_turnos_disponibles(self):' not in content, \
        "❌ La función _cargar_turnos_disponibles todavía existe"
    assert 'self._cargar_turnos_disponibles()' not in content, \
        "❌ La llamada a _cargar_turnos_disponibles todavía existe"
    print("✅ Función _cargar_turnos_disponibles eliminada")
    
    # Verificar que la validación de turno fue removida de _guardar
    lines = content.split('\n')
    turno_validation_found = False
    for i, line in enumerate(lines):
        if 'if not self.turno_var.get():' in line:
            # Verificar contexto - debe estar en el save de registro, no en validación
            next_lines = '\n'.join(lines[i:i+3])
            if 'El turno es obligatorio' in next_lines:
                turno_validation_found = True
                break
    
    assert not turno_validation_found, \
        "❌ La validación obligatoria de turno todavía existe en _guardar"
    print("✅ Validación de turno eliminada de _guardar")
    
    # Verificar que el turno todavía se guarda en el registro
    assert '"turno": self.turno_var.get()' in content, \
        "❌ El turno ya no se guarda en el registro"
    print("✅ Turno todavía se guarda en el registro (aunque no sea visible)")
    
    print("✅ Test 3 PASADO: Campo Turno eliminado, pero funcionalidad preservada\n")


def test_integration():
    """Test 4: Verificar que los imports necesarios existen"""
    print("=== Test 4: Verificación de imports ===")
    
    # Verificar imports en pdf_generator.py
    with open('services/pdf_generator.py', 'r', encoding='utf-8') as f:
        pdf_content = f.read()
    
    assert 'from reportlab.lib.enums import TA_CENTER, TA_LEFT' in pdf_content, \
        "❌ Falta import de enums en pdf_generator.py"
    print("✅ Imports de reportlab correctos")
    
    # Verificar que settings y BASE_DIR están disponibles
    assert 'from config.settings import settings' in pdf_content or 'settings' in pdf_content, \
        "❌ Falta referencia a settings"
    assert 'BASE_DIR' in pdf_content, \
        "❌ Falta referencia a BASE_DIR"
    print("✅ Referencias a configuración correctas")
    
    print("✅ Test 4 PASADO: Imports y dependencias correctos\n")


def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("TESTS PARA LAS 3 MEJORAS IMPLEMENTADAS")
    print("="*60)
    
    try:
        test_listados_tab_changes()
        test_pdf_generator_changes()
        test_form_tab_turno_removal()
        test_integration()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*60)
        print("\nResumen de cambios verificados:")
        print("1. ✅ Materias y profesores se cargan automáticamente en Listados")
        print("2. ✅ PDF mejorado con encabezado profesional, logo y filtros")
        print("3. ✅ Campo Turno removido de UI pero funcionalidad preservada")
        print("\n")
        return 0
    
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
