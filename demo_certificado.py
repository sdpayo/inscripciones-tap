#!/usr/bin/env python3
"""
Demo: Generar un certificado de muestra para verificar el diseño.

Este script genera un certificado con datos de ejemplo que demuestran
todas las características del diseño institucional.
"""
from services.pdf_generator import generar_certificado_pdf
from datetime import datetime
import os

def main():
    """Genera certificado de demostración."""
    
    print("="*70)
    print("GENERACIÓN DE CERTIFICADO DE INSCRIPCIÓN - DEMO")
    print("="*70)
    
    # Datos de ejemplo realistas
    registro_demo = {
        "nombre": "María Alejandra",
        "apellido": "González Fernández",
        "dni": "35.123.456",
        "legajo": "2025001",
        "edad": "22",
        "direccion": "Av. San Martín 1234, Salta Capital",
        "email": "maria.gonzalez@example.com",
        "turno": "Mañana",
        "anio": "2",
        "materia": "Piano - Nivel Intermedio",
        "profesor": "Prof. Ana María Rodríguez",
        "comision": "A",
        "horario": "Lunes y Miércoles 9:00 - 11:00",
        "seguro_escolar": "Sí",
        "obra_social": "OSDE Plan 210",
        "fecha_inscripcion": "2025-03-15T10:30:00"
    }
    
    print("\n📋 Datos del certificado:")
    print(f"   Alumno: {registro_demo['nombre']} {registro_demo['apellido']}")
    print(f"   DNI: {registro_demo['dni']}")
    print(f"   Legajo: {registro_demo['legajo']}")
    print(f"   Materia: {registro_demo['materia']}")
    print(f"   Profesor: {registro_demo['profesor']}")
    print(f"   Turno: {registro_demo['turno']} - {registro_demo['horario']}")
    
    print("\n🔄 Generando certificado PDF...")
    
    ok, resultado = generar_certificado_pdf(registro_demo)
    
    if ok:
        print(f"\n✅ ¡Certificado generado exitosamente!")
        print(f"📄 Ubicación: {resultado}")
        
        # Mostrar tamaño del archivo
        if os.path.exists(resultado):
            size_kb = os.path.getsize(resultado) / 1024
            print(f"📊 Tamaño: {size_kb:.1f} KB")
            
            if size_kb > 100:
                print("   ✓ El archivo contiene imágenes (logo y firma)")
            else:
                print("   ⚠ El archivo es pequeño (sin imágenes)")
        
        print("\n📋 Características del certificado:")
        print("   ✓ Logo ESM arriba a la izquierda")
        print("   ✓ Encabezado con nombre de escuela")
        print("   ✓ Sección 'Datos del Estudiante'")
        print("   ✓ Sección 'Datos de Inscripción'")
        print("   ✓ Firma gráfica al pie")
        print("   ✓ Información del rector")
        print("   ✓ Pie de página legal")
        
        print("\n" + "="*70)
        print("Para visualizar el certificado, abra el archivo PDF generado.")
        print("="*70)
        
    else:
        print(f"\n❌ Error al generar certificado:")
        print(f"   {resultado}")

if __name__ == "__main__":
    main()
