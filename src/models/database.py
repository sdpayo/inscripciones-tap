"""Database management for the application."""
import sqlite3
from typing import List, Optional
from contextlib import contextmanager
from .student import Student
from ..config import Config


class Database:
    """SQLite database manager."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        self.db_path = db_path or str(Config.DATABASE_PATH)
        self.create_tables()
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create_tables(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    dni TEXT NOT NULL UNIQUE,
                    fecha_nacimiento TEXT NOT NULL,
                    email TEXT NOT NULL,
                    telefono TEXT NOT NULL,
                    direccion TEXT NOT NULL,
                    ciudad TEXT DEFAULT 'Salta',
                    provincia TEXT DEFAULT 'Salta',
                    codigo_postal TEXT,
                    contacto_emergencia_nombre TEXT,
                    contacto_emergencia_telefono TEXT,
                    contacto_emergencia_relacion TEXT,
                    instrumento TEXT,
                    nivel TEXT,
                    experiencia_previa TEXT,
                    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estado TEXT DEFAULT 'Pendiente',
                    notas TEXT
                )
            """)
            conn.commit()
    
    def add_student(self, student: Student) -> int:
        """Add a new student to the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO students (
                    nombre, apellido, dni, fecha_nacimiento, email, telefono,
                    direccion, ciudad, provincia, codigo_postal,
                    contacto_emergencia_nombre, contacto_emergencia_telefono,
                    contacto_emergencia_relacion, instrumento, nivel,
                    experiencia_previa, fecha_inscripcion, estado, notas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student.nombre, student.apellido, student.dni,
                student.fecha_nacimiento, student.email, student.telefono,
                student.direccion, student.ciudad, student.provincia,
                student.codigo_postal, student.contacto_emergencia_nombre,
                student.contacto_emergencia_telefono, student.contacto_emergencia_relacion,
                student.instrumento, student.nivel, student.experiencia_previa,
                student.fecha_inscripcion, student.estado, student.notas
            ))
            conn.commit()
            return cursor.lastrowid
    
    def update_student(self, student: Student):
        """Update an existing student."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE students SET
                    nombre=?, apellido=?, dni=?, fecha_nacimiento=?, email=?, telefono=?,
                    direccion=?, ciudad=?, provincia=?, codigo_postal=?,
                    contacto_emergencia_nombre=?, contacto_emergencia_telefono=?,
                    contacto_emergencia_relacion=?, instrumento=?, nivel=?,
                    experiencia_previa=?, estado=?, notas=?
                WHERE id=?
            """, (
                student.nombre, student.apellido, student.dni,
                student.fecha_nacimiento, student.email, student.telefono,
                student.direccion, student.ciudad, student.provincia,
                student.codigo_postal, student.contacto_emergencia_nombre,
                student.contacto_emergencia_telefono, student.contacto_emergencia_relacion,
                student.instrumento, student.nivel, student.experiencia_previa,
                student.estado, student.notas, student.id
            ))
            conn.commit()
    
    def delete_student(self, student_id: int):
        """Delete a student by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
            conn.commit()
    
    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """Get a student by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
            row = cursor.fetchone()
            if row:
                return Student(**dict(row))
            return None
    
    def get_student_by_dni(self, dni: str) -> Optional[Student]:
        """Get a student by DNI."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE dni=?", (dni,))
            row = cursor.fetchone()
            if row:
                return Student(**dict(row))
            return None
    
    def get_all_students(self) -> List[Student]:
        """Get all students."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students ORDER BY fecha_inscripcion DESC")
            rows = cursor.fetchall()
            return [Student(**dict(row)) for row in rows]
    
    def search_students(self, query: str) -> List[Student]:
        """Search students by name, DNI, or email."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT * FROM students 
                WHERE nombre LIKE ? OR apellido LIKE ? OR dni LIKE ? OR email LIKE ?
                ORDER BY fecha_inscripcion DESC
            """, (search_pattern, search_pattern, search_pattern, search_pattern))
            rows = cursor.fetchall()
            return [Student(**dict(row)) for row in rows]
    
    def get_students_by_status(self, estado: str) -> List[Student]:
        """Get students by status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM students WHERE estado=? ORDER BY fecha_inscripcion DESC",
                (estado,)
            )
            rows = cursor.fetchall()
            return [Student(**dict(row)) for row in rows]
