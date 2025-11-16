"""Convierte instruments.json de dict a list."""
import json
from config.settings import INSTRUMENTS_FILE
from pathlib import Path
import shutil

def convertir_instruments():
    if not INSTRUMENTS_FILE.exists():
        print(f"ERROR: {INSTRUMENTS_FILE} no existe")
        return
    
    print("=" * 60)
    print("CONVERTIR INSTRUMENTS.JSON")
    print("=" * 60)
    
    # Backup
    backup = INSTRUMENTS_FILE.with_suffix('.json.backup')
    shutil.copy(INSTRUMENTS_FILE, backup)
    print(f"\nOK: Backup creado: {backup.name}")
    
    # Cargar datos actuales
    with open(INSTRUMENTS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\nFormato actual: {type(data).__name__}")
    
    if isinstance(data, dict):
        # Convertir dict a list
        lista_materias = []
        
        # Caso 1: {"materias": [...]}
        if "materias" in data and isinstance(data["materias"], list):
            lista_materias = data["materias"]
            print("Detectado: dict con clave 'materias'")
        
        # Caso 2: {"materia1": {...}, "materia2": {...}}
        elif all(isinstance(v, dict) for v in data.values()):
            for key, value in data.items():
                # Si el dict interno no tiene 'materia', usar la clave como nombre
                if "materia" not in value:
                    value["materia"] = key
                lista_materias.append(value)
            print("Detectado: dict de dicts (convertido a lista)")
        
        # Caso 3: Otros formatos
        else:
            print("\nFormato no reconocido. Estructura del dict:")
            estructura = json.dumps(data, indent=2, ensure_ascii=False)[:500]
            print(estructura)
            print("\n...")
            print("\nComo queres convertirlo?")
            print("1. Usar valores del dict (ignorar claves)")
            print("2. Extraer lista de una clave especifica")
            print("3. Cancelar")
            
            opcion = input("\nOpcion: ").strip()
            
            if opcion == "1":
                lista_materias = [v for v in data.values() if isinstance(v, dict)]
            elif opcion == "2":
                clave = input("Nombre de la clave: ").strip()
                if clave in data and isinstance(data[clave], list):
                    lista_materias = data[clave]
                else:
                    print("ERROR: Clave no valida")
                    return
            else:
                print("Cancelado")
                return
        
        print(f"\nMaterias extraidas: {len(lista_materias)}")
        
        if lista_materias:
            # Mostrar muestra
            print("\nMuestra de las primeras 3 materias:")
            for i, mat in enumerate(lista_materias[:3], 1):
                nombre = mat.get('materia', 'Sin nombre')
                profesor = mat.get('profesor', 'N/A')
                comision = mat.get('comision', 'N/A')
                print(f"\n  {i}. {nombre}")
                print(f"     Profesor: {profesor}")
                print(f"     Comision: {comision}")
            
            # Confirmar
            resp = input("\nGuardar en este formato? (S/n): ").strip().lower()
            if resp == 'n':
                print("Cancelado")
                return
            
            # Guardar
            with open(INSTRUMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(lista_materias, f, indent=2, ensure_ascii=False)
            
            print(f"\nOK: Convertido correctamente")
            print(f"*
