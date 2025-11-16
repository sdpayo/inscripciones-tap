"""Student data model."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Student:
    """Student registration data model."""
    
    # Personal information
    nombre: str
    apellido: str
    dni: str
    fecha_nacimiento: str
    email: str
    telefono: str
    
    # Address
    direccion: str
    ciudad: str = "Salta"
    provincia: str = "Salta"
    codigo_postal: str = ""
    
    # Emergency contact
    contacto_emergencia_nombre: str = ""
    contacto_emergencia_telefono: str = ""
    contacto_emergencia_relacion: str = ""
    
    # Academic information
    instrumento: str = ""
    nivel: str = ""
    experiencia_previa: str = ""
    
    # System fields
    id: Optional[int] = None
    fecha_inscripcion: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    estado: str = "Pendiente"  # Pendiente, Aprobado, Rechazado
    notas: str = ""
    
    def to_dict(self):
        """Convert student to dictionary."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'dni': self.dni,
            'fecha_nacimiento': self.fecha_nacimiento,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'ciudad': self.ciudad,
            'provincia': self.provincia,
            'codigo_postal': self.codigo_postal,
            'contacto_emergencia_nombre': self.contacto_emergencia_nombre,
            'contacto_emergencia_telefono': self.contacto_emergencia_telefono,
            'contacto_emergencia_relacion': self.contacto_emergencia_relacion,
            'instrumento': self.instrumento,
            'nivel': self.nivel,
            'experiencia_previa': self.experiencia_previa,
            'fecha_inscripcion': self.fecha_inscripcion,
            'estado': self.estado,
            'notas': self.notas
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create student from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def get_full_name(self):
        """Get full name."""
        return f"{self.nombre} {self.apellido}"
