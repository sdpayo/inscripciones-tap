"""Validadores de datos de inscripción."""
import re
from datetime import datetime


def validar_dni(dni):
    """
    Valida formato de DNI argentino.
    Args:
        dni (str): DNI a validar
    Returns: bool
    """
    if not dni:
        return False
    
    # Remover puntos y espacios
    dni_clean = dni.replace(".", "").replace(" ", "").strip()
    
    # Debe ser numérico y tener 7-8 dígitos
    if not dni_clean.isdigit():
        return False
    
    if len(dni_clean) < 7 or len(dni_clean) > 8:
        return False
    
    return True


def validar_email(email):
    """
    Valida formato de email.
    Args:
        email (str): Email a validar
    Returns: bool
    """
    if not email:
        return True  # Email es opcional
    
    # Regex básico para email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def validar_telefono(telefono):
    """
    Valida formato de teléfono (flexible).
    Args:
        telefono (str): Teléfono a validar
    Returns: bool
    """
    if not telefono:
        return True  # Teléfono es opcional
    
    # Remover caracteres comunes
    tel_clean = telefono.replace("-", "").replace(" ", "").replace("(", "").replace(")", "").strip()
    
    # Debe tener al menos 7 dígitos
    digits = "".join(c for c in tel_clean if c.isdigit())
    
    return len(digits) >= 7


def validar_edad_minima(edad, minima=5):
    """
    Valida edad mínima.
    Args:
        edad (int): Edad a validar
        minima (int): Edad mínima requerida
    Returns: bool
    """
    try:
        return int(edad) >= minima
    except (ValueError, TypeError):
        return False


def validar_cupo_disponible(materia, profesor=None, comision=None):
    """
    Valida si hay cupo disponible en una materia.
    Args:
        materia (str): Nombre de la materia
        profesor (str, optional): Nombre del profesor
        comision (str, optional): Nombre de la comisión
    Returns: tuple(bool, str) - (es_valido, mensaje)
    """
    from models.materias import tiene_cupo_disponible
    from config.settings import settings
    
    # Si está deshabilitado el check de cupos, siempre es válido
    if not settings.get("app.check_cupos", True):
        return True, "Verificación de cupos deshabilitada"
    
    return tiene_cupo_disponible(materia, profesor, comision)


def validar_datos_inscripcion(datos):
    """
    Valida datos completos de inscripción.
    Args:
        datos (dict): Datos a validar
    Returns: tuple(bool, str) - (es_valido, mensaje_error)
    """
    # Campos obligatorios
    campos_obligatorios = {
        "nombre": "Nombre",
        "apellido": "Apellido",
        "dni": "DNI",
        "edad": "Edad",
        "turno": "Turno",
        "anio": "Año",
        "materia": "Materia",
        "profesor": "Profesor",
        "comision": "Comisión"
    }
    
    # Verificar campos obligatorios
    for campo, nombre in campos_obligatorios.items():
        valor = datos.get(campo)
        if not valor or (isinstance(valor, str) and not valor.strip()):
            return False, f"El campo '{nombre}' es obligatorio."
    
    # Validar DNI
    if not validar_dni(datos.get("dni", "")):
        return False, "El DNI debe tener 7-8 dígitos numéricos."
    
    # Validar edad
    try:
        edad = int(datos.get("edad", 0))
        if edad <= 0:
            return False, "La edad debe ser mayor a 0."
        if not validar_edad_minima(edad, 5):
            return False, "La edad mínima es 5 años."
    except (ValueError, TypeError):
        return False, "La edad debe ser un número válido."
    
    # Validar email si existe
    email = datos.get("email", "").strip()
    if email and not validar_email(email):
        return False, "El formato del email no es válido."
    
    # Validar teléfono si existe
    telefono = datos.get("telefono", "").strip()
    if telefono and not validar_telefono(telefono):
        return False, "El formato del teléfono no es válido."
    
    # Validar cupo
    ok_cupo, msg_cupo = validar_cupo_disponible(
        datos.get("materia"),
        datos.get("profesor"),
        datos.get("comision")
    )
    
    if not ok_cupo:
        # Si no hay cupo, preguntar si quiere lista de espera
        # (esto se maneja en la UI, aquí solo informamos)
        return False, f"⚠️ {msg_cupo}\n\n¿Desea inscribir en lista de espera?"
    
    return True, "Datos válidos"


def validar_campos_certificado(datos):
    """
    Valida datos necesarios para generar certificado.
    Args:
        datos (dict): Datos del alumno
    Returns: tuple(bool, str) - (es_valido, mensaje_error)
    """
    from config.settings import settings
    
    # Campos mínimos requeridos
    if not datos.get("nombre") or not datos.get("apellido"):
        return False, "Faltan nombre o apellido del alumno."
    
    if not datos.get("dni"):
        return False, "Falta DNI del alumno."
    
    if not datos.get("materia"):
        return False, "Falta materia de inscripción."
    
    # Verificar seguro escolar si está configurado
    if settings.get("app.require_seguro_escolar", True):
        if datos.get("seguro_escolar", "No") != "Sí":
            return False, "El alumno debe tener seguro escolar para generar certificado."
    
    return True, "Datos válidos para certificado"


def normalizar_nombre(nombre):
    """
    Normaliza nombre (capitalización).
    Args:
        nombre (str): Nombre a normalizar
    Returns: str
    """
    if not nombre:
        return ""
    
    # Title case pero respetando casos especiales
    palabras = nombre.strip().split()
    palabras_normalizadas = []
    
    for palabra in palabras:
        # Preservar siglas (ej: DNI, USA)
        if palabra.isupper() and len(palabra) <= 4:
            palabras_normalizadas.append(palabra)
        # Preservar nombres con apóstrofe (ej: D'Angelo)
        elif "'" in palabra:
            partes = palabra.split("'")
            palabras_normalizadas.append("'".join(p.capitalize() for p in partes))
        else:
            palabras_normalizadas.append(palabra.capitalize())
    
    return " ".join(palabras_normalizadas)


def normalizar_datos_inscripcion(datos):
    """
    Normaliza datos de inscripción (capitalización, espacios, etc.).
    Args:
        datos (dict): Datos a normalizar
    Returns: dict
    """
    datos_normalizados = datos.copy()
    
    # Normalizar nombres
    campos_nombre = ["nombre", "apellido", "nombre_padre", "nombre_madre"]
    for campo in campos_nombre:
        if campo in datos_normalizados:
            datos_normalizados[campo] = normalizar_nombre(datos_normalizados[campo])
    
    # Limpiar espacios en campos de texto
    for campo in datos_normalizados:
        if isinstance(datos_normalizados[campo], str):
            datos_normalizados[campo] = datos_normalizados[campo].strip()
    
    # Normalizar DNI (sin puntos)
    if "dni" in datos_normalizados:
        dni = datos_normalizados["dni"]
        datos_normalizados["dni"] = dni.replace(".", "").replace(" ", "").strip()
    
    return datos_normalizados


def validar_dni_duplicado(dni, excluir_id=None):
    """
    Verifica si un DNI ya está registrado.
    Args:
        dni (str): DNI a verificar
        excluir_id (str, optional): ID de registro a excluir (para edición)
    Returns: tuple(bool, str) - (es_duplicado, mensaje)
    """
    from database.csv_handler import buscar_por_dni
    
    registros = buscar_por_dni(dni)
    
    # Filtrar el registro que se está editando
    if excluir_id:
        registros = [r for r in registros if r.get("id") != excluir_id]
    
    if registros:
        # Listar materias donde ya está inscripto
        materias = [r.get("materia", "N/A") for r in registros]
        materias_str = ", ".join(materias[:3])  # Mostrar max 3
        if len(materias) > 3:
            materias_str += f" (+{len(materias)-3} más)"
        
        return True, f"DNI ya registrado en: {materias_str}"
    
    return False, "DNI disponible"


def sanitizar_texto(texto, max_length=None):
    """
    Sanitiza texto para evitar problemas en CSV/PDF.
    Args:
        texto (str): Texto a sanitizar
        max_length (int, optional): Longitud máxima
    Returns: str
    """
    if not texto:
        return ""
    
    # Remover caracteres problemáticos
    texto_limpio = texto.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    
    # Reducir espacios múltiples
    texto_limpio = " ".join(texto_limpio.split())
    
    # Truncar si es necesario
    if max_length and len(texto_limpio) > max_length:
        texto_limpio = texto_limpio[:max_length-3] + "..."
    
    return texto_limpio