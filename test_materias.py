# test_materias.py
from models.materias import (
    get_materias_list, get_materia_config,
    get_professors_for_materia, get_commissions_for_materia,
    get_commission_quota, remaining_cupos,
    build_global_professors_list
)

# Test listar materias
materias = get_materias_list()
print(f"✅ {len(materias)} materias cargadas")
if materias:
    print(f"   Ejemplo: {materias[0]}")

# Test config de materia (usa una de tu instruments.json)
if materias:
    cfg = get_materia_config(materias[0])
    if cfg:
        print(f"✅ Config cargada para '{materias[0]}'")
        print(f"   Tipo: {cfg.get('type')}")
        print(f"   Profesores: {len(cfg.get('professors', {}))}")

# Test profesores globales
profs = build_global_professors_list()
print(f"✅ {len(profs)} profesores en total")
if profs:
    print(f"   Ejemplo: {profs[0]}")

# Test cupos (si existe comisión definida)
if materias:
    comisiones = get_commissions_for_materia(materias[0])
    if comisiones:
        quota = get_commission_quota(materias[0], comisiones[0])
        print(f"✅ Cupo comisión '{comisiones[0]}': {quota}")
        rem = remaining_cupos(materias[0], comisiones[0])
        print(f"   Disponibles: {rem}")

print("\n🎉 Models/Materias funciona!")