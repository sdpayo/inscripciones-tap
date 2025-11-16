"""Funciones auxiliares sin dependencias pesadas."""
import unicodedata
import re

EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")

def _norm_key(s):
    """Normaliza strings para matching: minúsculas, sin acentos."""
    if not s:
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return " ".join(s.split())

def _sanitize_filename(s: str) -> str:
    """Sanea nombres de archivo (permite puntos para extensiones)."""
    s = s.strip().replace(" ", "_")
    return "".join(c for c in s if c.isalnum() or c in ("_", "-", "."))  # ← Agregado el punto

def _sanitize_pdf_text(s):
    """Normaliza texto para fpdf (latin-1 compatible)."""
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    
    s = s.strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = "".join(ch if ord(ch) >= 32 else " " for ch in s)
    
    try:
        s.encode("latin-1")
        return s
    except:
        return s.encode("latin-1", "replace").decode("latin-1")

def validar_email(email: str) -> bool:
    """Valida formato de email."""
    return bool(EMAIL_RE.match(email.strip())) if email else False