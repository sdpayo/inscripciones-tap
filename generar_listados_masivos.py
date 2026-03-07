"""
Script para generar listados PDF masivos de TODOS los profesores y cátedras.
Lee directamente desde data/inscripciones_sheets.csv y genera un PDF por cada combinación materia-profesor.
"""

import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from services.pdf_generator import generar_listado_pdf
from config.settings import DATA_DIR

def cargar_csv_completo(csv_path):
    """Carga CSV completo sin filtros."""
    registros = []
    print(f"[LOAD] Cargando desde {csv_path}...")
    
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            registros.append(dict(row))
    
    print(f"[LOAD] ✓ Cargados {len(registros)} registros")
    return registros

def agrupar_por_materia_profesor_comision(registros):
    """
    Agrupa registros por combinación de materia + profesor + comisión NORMALIZADAS.
    Retorna dict: {(materia, profesor, comision): [registros]}
    """
    # Primero agrupar por versión normalizada
    grupos_normalizados = defaultdict(list)
    # Guardar la primera variante encontrada para cada versión normalizada
    nombres_originales = {}
    
    for reg in registros:
        materia = str(reg.get('materia', '')).strip()
        profesor = str(reg.get('profesor', '')).strip()
        comision = str(reg.get('comision', '')).strip()
        
        # Saltar registros sin materia o profesor
        if not materia or not profesor:
            continue
        
        # Normalizar para agrupar (lowercase)
        materia_norm = materia.lower()
        profesor_norm = profesor.lower()
        comision_norm = comision.lower()
        key_norm = (materia_norm, profesor_norm, comision_norm)
        
        # Guardar primera variante original para usar en nombre de archivo
        if key_norm not in nombres_originales:
            nombres_originales[key_norm] = (materia, profesor, comision)
        
        grupos_normalizados[key_norm].append(reg)
    
    # Convertir a dict con nombres originales como keys
    grupos_finales = {}
    for key_norm, regs in grupos_normalizados.items():
        nombres_orig = nombres_originales[key_norm]
        grupos_finales[nombres_orig] = regs
    
    return grupos_finales

def generar_listados_masivos(csv_path=None, output_dir=None):
    """
    Genera PDFs para TODAS las combinaciones materia-profesor.
    
    Args:
        csv_path: Ruta al CSV (default: data/inscripciones_sheets.csv)
        output_dir: Carpeta de salida (default: data/reports/)
    """
    # Configurar rutas
    if csv_path is None:
        csv_path = DATA_DIR / "inscripciones_sheets.csv"
    
    if output_dir is None:
        output_dir = DATA_DIR / "reports"
    
    # Crear carpeta de salida
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*70)
    print("GENERACIÓN MASIVA DE LISTADOS PDF")
    print("="*70 + "\n")
    
    # Cargar datos
    registros = cargar_csv_completo(csv_path)
    
    if not registros:
        print("❌ No se encontraron registros en el CSV")
        return
    
    # Agrupar por materia-profesor-comisión
    print("\n[AGRUPANDO] Por materia, profesor y comisión...")
    grupos = agrupar_por_materia_profesor_comision(registros)
    print(f"[AGRUPANDO] ✓ Encontradas {len(grupos)} combinaciones materia-profesor-comisión\n")
    
    # Generar PDF para cada grupo
    exitosos = 0
    fallidos = 0
    
    for idx, ((materia, profesor, comision), regs_grupo) in enumerate(sorted(grupos.items()), 1):
        # Limpiar nombres para archivo
        materia_clean = materia.replace('/', '_').replace('\\', '_').replace(':', '_')[:40]
        profesor_clean = profesor.replace('/', '_').replace('\\', '_').replace(':', '_')[:30]
        comision_clean = comision.replace('/', '_').replace('\\', '_').replace(':', '_')[:10] if comision else 'SinCom'
        
        filename = f"{materia_clean}_{profesor_clean}_{comision_clean}.pdf"
        output_path = output_dir / filename
        
        print(f"[{idx}/{len(grupos)}] Generando: {materia} - {profesor} - Com: {comision or '(Sin comisión)'}")
        print(f"           Estudiantes: {len(regs_grupo)}")
        
        try:
            ok, msg = generar_listado_pdf(
                regs_grupo,
                str(output_path),
                filtro_materia=materia,
                filtro_profesor=profesor
            )
            
            if ok:
                print(f"           ✓ {msg}")
                exitosos += 1
            else:
                print(f"           ❌ Error: {msg}")
                fallidos += 1
        except Exception as e:
            print(f"           ❌ Excepción: {e}")
            fallidos += 1
        
        print()
    
    # Resumen
    print("="*70)
    print("RESUMEN")
    print("="*70)
    print(f"✓ PDFs exitosos:     {exitosos}")
    print(f"❌ PDFs fallidos:    {fallidos}")
    print(f"📁 Carpeta salida:   {output_dir}")
    print("="*70 + "\n")

def generar_listado_por_materia(materia, csv_path=None, output_dir=None):
    """
    Genera un PDF para una materia específica (todos los profesores).
    
    Args:
        materia: Nombre de la materia
        csv_path: Ruta al CSV
        output_dir: Carpeta de salida
    """
    if csv_path is None:
        csv_path = DATA_DIR / "inscripciones_sheets.csv"
    
    if output_dir is None:
        output_dir = DATA_DIR / "reports"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Cargar y filtrar
    registros = cargar_csv_completo(csv_path)
    filtrados = [r for r in registros if str(r.get('materia', '')).strip().lower() == materia.strip().lower()]
    
    if not filtrados:
        print(f"❌ No se encontraron registros para la materia: {materia}")
        return
    
    # Generar PDF
    materia_clean = materia.replace('/', '_').replace('\\', '_').replace(':', '_')[:50]
    filename = f"{materia_clean}_completo.pdf"
    output_path = output_dir / filename
    
    print(f"\n[GENERANDO] {materia}")
    print(f"           Estudiantes: {len(filtrados)}")
    
    ok, msg = generar_listado_pdf(
        filtrados,
        str(output_path),
        filtro_materia=materia,
        filtro_profesor=None
    )
    
    if ok:
        print(f"           ✓ {msg}\n")
    else:
        print(f"           ❌ {msg}\n")

def generar_listado_por_profesor(profesor, csv_path=None, output_dir=None):
    """
    Genera un PDF para un profesor específico (todas sus materias).
    
    Args:
        profesor: Nombre del profesor
        csv_path: Ruta al CSV
        output_dir: Carpeta de salida
    """
    if csv_path is None:
        csv_path = DATA_DIR / "inscripciones_sheets.csv"
    
    if output_dir is None:
        output_dir = DATA_DIR / "reports"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Cargar y filtrar
    registros = cargar_csv_completo(csv_path)
    filtrados = [r for r in registros if str(r.get('profesor', '')).strip().lower() == profesor.strip().lower()]
    
    if not filtrados:
        print(f"❌ No se encontraron registros para el profesor: {profesor}")
        return
    
    # Generar PDF
    profesor_clean = profesor.replace('/', '_').replace('\\', '_').replace(':', '_')[:50]
    filename = f"{profesor_clean}_completo.pdf"
    output_path = output_dir / filename
    
    print(f"\n[GENERANDO] {profesor}")
    print(f"           Estudiantes: {len(filtrados)}")
    
    ok, msg = generar_listado_pdf(
        filtrados,
        str(output_path),
        filtro_materia=None,
        filtro_profesor=profesor
    )
    
    if ok:
        print(f"           ✓ {msg}\n")
    else:
        print(f"           ❌ {msg}\n")

if __name__ == "__main__":
    import sys
    
    print("\n🎵 GENERADOR MASIVO DE LISTADOS - ESM N°6003\n")
    
    if len(sys.argv) > 1:
        # Modo específico
        modo = sys.argv[1].lower()
        
        if modo == "materia" and len(sys.argv) > 2:
            materia = " ".join(sys.argv[2:])
            generar_listado_por_materia(materia)
        
        elif modo == "profesor" and len(sys.argv) > 2:
            profesor = " ".join(sys.argv[2:])
            generar_listado_por_profesor(profesor)
        
        else:
            print("Uso:")
            print("  python generar_listados_masivos.py                  # Genera TODOS")
            print("  python generar_listados_masivos.py materia <nombre> # Solo una materia")
            print("  python generar_listados_masivos.py profesor <nombre># Solo un profesor")
    
    else:
        # Modo masivo: generar TODOS
        generar_listados_masivos()
    
    print("\n✅ Finalizado\n")
    print("Presiona Enter para salir...")
    input()
