#!/usr/bin/env python3
"""
Genera instruments.json a partir de Materias_TAP.csv.

Este generador:
 - Lee cada fila del CSV y asigna la DIV (Div.) como comisión.
 - Si detecta que una comisión tiene un docente específico, escribe la comisión
   en la sección 'commissions' con valor {"capacity": <int_or_null>, "professor": "<Docente>"}.
 - Además, añade en la sección 'professors' del instrumento el docente y sus 'turnos' si están.
 - De esta forma el cargador (models.materias) puede respetar la asociación
   comision <-> profesor y no mostrar todas las comisiones para cada profesor.
"""
import csv
import json
import sys
from pathlib import Path
from collections import defaultdict

def parse_int_safe(v):
    if v is None:
        return None
    s = str(v).strip()
    if s == "":
        return None
    try:
        return int(s)
    except Exception:
        s2 = s.replace(",", "").replace(".", "")
        try:
            return int(s2)
        except Exception:
            return None

def normalize(s):
    if s is None:
        return ""
    return str(s).strip()

def main(csv_path, out_path):
    csv_path = Path(csv_path)
    out_path = Path(out_path)

    if not csv_path.exists():
        print(f"CSV no encontrado: {csv_path}")
        return 1

    materias = {}

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            año_raw = normalize(row.get("Año") or "")
            tipo_raw = normalize(row.get("Tipo") or "")
            docente = normalize(row.get("Docente") or "")
            asignatura = normalize(row.get("Asignatura") or "")
            div = normalize(row.get("Div.") or row.get("Div") or "")
            cupos_raw = row.get("CUPOS") or row.get("Cupos") or ""
            turno = normalize(row.get("Turno") or "")

            if asignatura == "":
                continue

            if asignatura not in materias:
                materias[asignatura] = {
                    "type": "individual" if tipo_raw.lower().startswith("ind") else "group",
                    "description": "",
                    "years": set(),
                    "allow_over": False if tipo_raw.lower().startswith("ind") else True,
                    "professors": {},
                    "commissions": {}
                }
            meta = materias[asignatura]

            # año
            try:
                if año_raw != "":
                    meta["years"].add(int(año_raw))
            except Exception:
                pass

            # profesor y turnos
            if docente:
                p = meta["professors"].get(docente, {})
                if turno:
                    existing = p.get("turnos", [])
                    if turno not in existing:
                        existing.append(turno)
                    p["turnos"] = existing
                meta["professors"][docente] = p

            # comision: si hay div, anotarla; si ya existe y no tiene profesor, y ahora hay docente -> asignar
            if div != "":
                cap = parse_int_safe(cupos_raw)
                existing = meta["commissions"].get(div)
                # preferir dict estructura para poder incluir professor
                if isinstance(existing, dict):
                    # si existing has no professor and now we have docente -> add
                    if not existing.get("professor") and docente:
                        existing["professor"] = docente
                    # if capacity empty and we have cap -> set
                    if (existing.get("capacity") is None) and (cap is not None):
                        existing["capacity"] = cap
                    meta["commissions"][div] = existing
                else:
                    # set a dict with capacity and professor if available
                    meta["commissions"][div] = {"capacity": cap, "professor": docente or None}
            else:
                # si no hay div (materia grupal sin división), no hacemos nada ahora
                pass

    # Postprocesar: convertir sets a listas y normalizar estructuras
    out = {}
    for materia, meta in sorted(materias.items(), key=lambda x: x[0].lower()):
        years_list = sorted(list(meta["years"]))
        if not years_list:
            years_list = []
        # asegurar comisiones: si vacío -> crear 'A': {"capacity": None}
        if not meta["commissions"]:
            meta["commissions"] = {"A": {"capacity": None, "professor": None}}

        profs = {}
        for p, info in sorted(meta["professors"].items(), key=lambda x: x[0].lower()):
            entry = {}
            if info.get("turnos"):
                entry["turnos"] = sorted(list(dict.fromkeys(info.get("turnos"))))
            profs[p] = entry

        comms = {}
        for c, v in sorted(meta["commissions"].items(), key=lambda x: str(x[0])):
            if isinstance(v, dict):
                comms[str(c)] = {}
                # conservar clave de capacidad bajo nombres comunes
                if v.get("capacity") is not None:
                    comms[str(c)]["capacity"] = int(v["capacity"])
                else:
                    comms[str(c)]["capacity"] = None
                if v.get("professor"):
                    comms[str(c)]["professor"] = v["professor"]
            else:
                # valor simple
                comms[str(c)] = v if v is not None else None

        out[materia] = {
            "type": meta["type"],
            "description": meta.get("description", ""),
            "years": years_list,
            "allow_over": bool(meta.get("allow_over", False)),
            "professors": profs,
            "commissions": comms
        }

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, sort_keys=False)

    print(f"Generado: {out_path} ({len(out)} materias)")
    return 0

if __name__ == "__main__":
    args = sys.argv[1:]
    csv_in = args[0] if len(args) >= 1 else "Materias_TAP.csv"
    json_out = args[1] if len(args) >= 2 else "instruments.json"
    sys.exit(main(csv_in, json_out))