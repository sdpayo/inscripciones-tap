"""Input validation functions."""
import re


def validate_dni(dni: str) -> bool:
    """
    Validate DNI (Argentine national ID).
    
    Args:
        dni: DNI string to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not dni:
        return False
    
    # Remove any non-digit characters
    dni_clean = re.sub(r'\D', '', dni)
    
    # DNI should be 7-8 digits
    return len(dni_clean) >= 7 and len(dni_clean) <= 8 and dni_clean.isdigit()


def validate_email(email: str) -> bool:
    """
    Validate email address.
    
    Args:
        email: Email string to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number.
    
    Args:
        phone: Phone string to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove any non-digit characters
    phone_clean = re.sub(r'\D', '', phone)
    
    # Phone should be at least 8 digits
    return len(phone_clean) >= 8 and phone_clean.isdigit()
