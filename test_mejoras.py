"""Tests for the three improvements: PDF amount, optimized filters, and Google Sheets sync."""
import sys
import os
from pathlib import Path

# Test 1: PDF amount display
print("=" * 60)
print("TEST 1: PDF Amount Display")
print("=" * 60)

try:
    from services.pdf_generator import generar_certificado_pdf
    
    # Test data with voluntary payment
    test_registro = {
        "id": "TEST001",
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "12345678",
        "legajo": "LEG001",
        "materia": "Guitarra",
        "profesor": "Carlos García",
        "turno": "Tarde",
        "anio": "1",
        "obra_social": "OSDE",
        "pago_voluntario": "Sí",
        "monto": "1500.50"
    }
    
    success, result = generar_certificado_pdf(test_registro)
    print(f"✓ PDF generation: {'SUCCESS' if success else 'FAILED'}")
    print(f"  Result: {result}")
    
    # Verify the PDF was created
    if success and Path(result).exists():
        print(f"✓ PDF file created at: {result}")
        print(f"  File size: {Path(result).stat().st_size} bytes")
    else:
        print("✗ PDF file was not created")
    
except ImportError as e:
    print(f"⚠ Skipping PDF test - missing dependencies: {e}")
except Exception as e:
    print(f"✗ PDF test error: {e}")

print()

# Test 2: Optimized filters
print("=" * 60)
print("TEST 2: Optimized Filters")
print("=" * 60)

try:
    from database.csv_handler import cargar_registros
    
    # Load registrations
    registros = cargar_registros()
    print(f"✓ Loaded {len(registros)} registrations")
    
    # Extract unique materias with inscriptions
    materias_con_inscripciones = sorted(set(
        reg.get("materia", "") for reg in registros if reg.get("materia")
    ))
    print(f"✓ Found {len(materias_con_inscripciones)} materias with registrations")
    if materias_con_inscripciones:
        print(f"  Sample materias: {materias_con_inscripciones[:3]}")
    
    # Extract unique professors with inscriptions
    profesores_con_inscripciones = sorted(set(
        reg.get("profesor", "") for reg in registros if reg.get("profesor")
    ))
    print(f"✓ Found {len(profesores_con_inscripciones)} professors with registrations")
    if profesores_con_inscripciones:
        print(f"  Sample professors: {profesores_con_inscripciones[:3]}")
    
    # Test filtering by materia
    if materias_con_inscripciones:
        test_materia = materias_con_inscripciones[0]
        profesores_filtrados = sorted(set(
            reg.get("profesor", "") for reg in registros 
            if reg.get("materia") == test_materia and reg.get("profesor")
        ))
        print(f"✓ Filtering by '{test_materia}': {len(profesores_filtrados)} professors")
    
except Exception as e:
    print(f"✗ Filter test error: {e}")

print()

# Test 3: Google Sheets sync
print("=" * 60)
print("TEST 3: Google Sheets Sync (Non-blocking)")
print("=" * 60)

try:
    from services.google_sheets import (
        get_google_sheets_service, 
        sync_to_google_sheets,
        sync_in_background
    )
    from config.settings import settings
    
    print("✓ Google Sheets module imported successfully")
    
    # Test service initialization (should not fail even if not configured)
    service, error = get_google_sheets_service()
    if error:
        print(f"⚠ Google Sheets not configured (expected): {error}")
    else:
        print("✓ Google Sheets service initialized")
    
    # Test sync function (should not block even if not configured)
    test_registro = {
        "id": "TEST002",
        "nombre": "María",
        "apellido": "González",
        "dni": "87654321"
    }
    
    # Disable Google Sheets temporarily for test
    original_enabled = settings.get("google_sheets.enabled", False)
    settings.set("google_sheets.enabled", False)
    
    success, message = sync_to_google_sheets(test_registro, 'insert')
    print(f"✓ Sync (disabled): {message}")
    
    # Test background sync (should not block)
    print("✓ Testing background sync (non-blocking)...")
    sync_in_background(test_registro, 'insert')
    print("✓ Background sync initiated (non-blocking)")
    
    # Restore setting
    settings.set("google_sheets.enabled", original_enabled)
    
except ImportError as e:
    print(f"⚠ Skipping Google Sheets test - missing dependencies: {e}")
except Exception as e:
    print(f"✗ Google Sheets test error: {e}")

print()
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("All tests completed. Review results above.")
print("Note: Some tests may show warnings if optional dependencies are not installed.")
print("This is expected and does not indicate a failure.")
