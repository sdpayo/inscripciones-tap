"""Servicio de envío de emails."""
import smtplib
from email.message import EmailMessage
from pathlib import Path
from config.settings import settings, DATA_DIR

# Configuración
SMTP_CONFIG_FILE = DATA_DIR / "config.json"
DEBUG = settings.get("app.debug", False)


def load_smtp_config():
    """Carga configuración SMTP desde config.json."""
    return settings.get_section("smtp")


def save_smtp_config(host, port, username, password, use_tls=True):
    """Guarda configuración SMTP."""
    smtp_config = {
        "host": host,
        "port": int(port),
        "username": username,
        "password": password,
        "use_tls": use_tls
    }
    settings.set_section("smtp", smtp_config)
    return True, "Configuración guardada"


def get_smtp_config():
    """Obtiene configuración SMTP."""
    return settings.get_section("smtp")


def send_certificado_via_email(registro, pdf_path, smtp_cfg=None):
    """
    Envía certificado por email.
    
    Args:
        registro (dict): Datos del estudiante
        pdf_path (str|Path): Ruta al PDF
        smtp_cfg (dict, optional): Config SMTP. Si None, carga desde archivo.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if smtp_cfg is None:
        smtp_cfg = load_smtp_config()
    
    # Validar destinatario
    to_addr = (registro.get("email") or "").strip()
    if not to_addr:
        return False, "El registro no tiene email configurado."
    
    # Validar configuración SMTP
    if not smtp_cfg.get("username") or not smtp_cfg.get("password"):
        return False, "SMTP no configurado (falta username/password)."
    
    # Parámetros SMTP
    host = smtp_cfg.get("host", "smtp.gmail.com")
    port = int(smtp_cfg.get("port", 587))
    user = smtp_cfg.get("username")
    pwd = smtp_cfg.get("password")
    use_tls = smtp_cfg.get("use_tls", True)
    from_name = smtp_cfg.get("from_name", "Escuela")
    from_addr = smtp_cfg.get("from_addr") or user
    
    # Construir mensaje
    msg = EmailMessage()
    subj = f"Certificado de inscripción - {registro.get('nombre','')} {registro.get('apellido','')}"
    msg["Subject"] = subj
    msg["From"] = f"{from_name} <{from_addr}>"
    msg["To"] = to_addr
    
    body = f"""Adjuntamos el certificado de inscripción de {registro.get('nombre','')} {registro.get('apellido','')}.

Saludos cordiales,
{from_name}"""
    msg.set_content(body)
    
    # Adjuntar PDF
    try:
        with open(pdf_path, "rb") as fh:
            data = fh.read()
        msg.add_attachment(
            data, 
            maintype="application", 
            subtype="pdf", 
            filename=Path(pdf_path).name
        )
    except Exception as e:
        return False, f"No se pudo abrir el PDF: {e}"
    
    # Enviar
    try:
        server = smtplib.SMTP(host, port, timeout=30)
        server.ehlo()
        if use_tls:
            server.starttls()
            server.ehlo()
        server.login(user, pwd)
        server.send_message(msg)
        server.quit()
        return True, f"Email enviado a {to_addr}"
    except Exception as e:
        return False, f"Error enviando email: {e}"


def test_smtp_connection(smtp_cfg):
    """
    Prueba conexión SMTP sin enviar email.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not smtp_cfg.get("username"):
        return False, "Falta username"
    
    host = smtp_cfg.get("host", "smtp.gmail.com")
    port = int(smtp_cfg.get("port", 587))
    user = smtp_cfg.get("username")
    pwd = smtp_cfg.get("password", "")
    use_tls = smtp_cfg.get("use_tls", True)
    
    try:
        server = smtplib.SMTP(host, port, timeout=15)
        server.ehlo()
        if use_tls:
            server.starttls()
            server.ehlo()
        if pwd:
            server.login(user, pwd)
            msg = "Conexión OK (login exitoso)"
        else:
            msg = "Conexión OK (sin login)"
        server.quit()
        return True, msg
    except Exception as e:
        return False, f"Error de conexión: {e}"