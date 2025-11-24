# diagnose_path.py
import os
from pathlib import Path
import traceback

# Pegá aquí la ruta EXACTA que ves en el Explorador (incluí la extension .json)
CANDIDATE = r"C:\Users\Damian\Documents\Cosas_de_ESM\inscrpciones_TAP_Patch\Inscripciones_TAP_main\inscripciones_modular\credentials.json"

def check(path):
    print(">>> CHECK:", path)
    print("repr: ", repr(path))
    try:
        print("abspath:", os.path.abspath(path))
        print("exists? ", os.path.exists(path))
        print("isfile? ", os.path.isfile(path))
        print("isdir?  ", os.path.isdir(path))
    except Exception:
        traceback.print_exc()

def list_parent(path):
    p = Path(path)
    parent = p.parent
    print("\nListando parent dir:", parent)
    try:
        for x in parent.iterdir():
            print(" -", x.name)
    except Exception as e:
        print("No se pudo listar:", e)

def try_variants(p):
    # raw as provided
    check(p)
    # doble backslash
    check(p.replace("\\", "\\\\"))
    # forward slashes
    check(p.replace("\\", "/"))
    # pathlib normalized
    check(str(Path(p)))
    # join from parent + basename
    parent = str(Path(p).parent)
    basename = Path(p).name
    check(os.path.join(parent, basename))

if __name__ == "__main__":
    print("Working dir:", os.getcwd())
    try_variants(CANDIDATE)
    list_parent(CANDIDATE)