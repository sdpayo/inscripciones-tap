"""Student registration form."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional, Callable
from ..models import Student, Database
from ..utils import validate_dni, validate_email, validate_phone


class StudentForm:
    """Form for creating/editing student information."""
    
    def __init__(
        self,
        parent,
        db: Database,
        student: Optional[Student] = None,
        on_save: Optional[Callable] = None
    ):
        """
        Initialize student form.
        
        Args:
            parent: Parent window
            db: Database instance
            student: Student to edit (None for new student)
            on_save: Callback function to call after saving
        """
        self.db = db
        self.student = student
        self.on_save = on_save
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Editar Estudiante" if student else "Nuevo Estudiante")
        self.window.geometry("600x750")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_form()
        
        # If editing, populate fields
        if student:
            self.populate_fields()
    
    def create_form(self):
        """Create form fields."""
        # Create scrollable canvas
        canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Personal Information
        ttk.Label(
            scrollable_frame,
            text="Información Personal",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
        
        ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5
        )
        
        row = 2
        
        # Nombre
        ttk.Label(scrollable_frame, text="Nombre:*").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.nombre_var, width=40).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )
        row += 1
        
        # Apellido
        ttk.Label(scrollable_frame, text="Apellido:*").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.apellido_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.apellido_var, width=40).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )
        row += 1
        
        # DNI
        ttk.Label(scrollable_frame, text="DNI:*").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.dni_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.dni_var, width=40).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )
        row += 1
        
        # Fecha de nacimiento
        ttk.Label(scrollable_frame, text="Fecha de Nacimiento:*").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        self.fecha_nac_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.fecha_nac_var, width=40).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )
        ttk.Label(scrollable_frame, text="(DD/MM/AAAA)", font=("Arial", 8)).grid(
            row=row+1, column=1, sticky="w", padx=10
        )
        row += 2
        
        # Email
        ttk.Label(scrollable_frame, text="Email:*").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.email_var, width=40).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )
        row += 1
        
        # Teléfono
        ttk.Label(scrollable_frame, text="Teléfono:*").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.telefono_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.telefono_var, width=40).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )
        row += 1
        
        # Address Section
        ttk.Label(
            scrollable_frame,
            text="Dirección",
            font=("Arial", 12, "bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 5))
        row += 1
        
        ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5
        )
        row += 1
        
        # Dirección
        ttk.Label(scrollable_frame, text="Dirección:*").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.direccion_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.direccion_var, width=40).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )
        row += 1
        
        # Ciudad
        ttk.Label(scrollable_frame, text="Ciudad:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.ciudad_var = tk.StringVar(value="Salta")
        ttk.Entry(scrollable_frame, textvariable=self.ciudad_var, width=40).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )
        row += 1
        
        # Provincia
        ttk.Label(scrollable_frame, text="Provincia:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.provincia_var = tk.StringVar(value="Salta")
        ttk.Entry(scrollable_frame, textvariable=self.provincia_var, width=40).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )
        row += 1
        
        # Código Postal
        ttk.Label(scrollable_frame, text="Código Postal:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.codigo_postal_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.codigo_postal_var, width=40).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )
        row += 1
        
        # Emergency Contact Section
        ttk.Label(
            scrollable_frame,
            text="Contacto de Emergencia",
            font=("Arial", 12, "bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 5))
        row += 1
        
        ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5
        )
        row += 1
        
        # Contacto emergencia nombre
        ttk.Label(scrollable_frame, text="Nombre:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.contacto_nombre_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.contacto_nombre_var, width=40).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )
        row += 1
        
        # Contacto emergencia teléfono
        ttk.Label(scrollable_frame, text="Teléfono:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.contacto_telefono_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.contacto_telefono_var, width=40).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )
        row += 1
        
        # Contacto emergencia relación
        ttk.Label(scrollable_frame, text="Relación:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.contacto_relacion_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.contacto_relacion_var, width=40).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )
        row += 1
        
        # Academic Information Section
        ttk.Label(
            scrollable_frame,
            text="Información Académica",
            font=("Arial", 12, "bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 5))
        row += 1
        
        ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5
        )
        row += 1
        
        # Instrumento
        ttk.Label(scrollable_frame, text="Instrumento:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.instrumento_var = tk.StringVar()
        instrumento_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.instrumento_var,
            values=[
                "Piano", "Guitarra", "Violín", "Viola", "Violonchelo", "Contrabajo",
                "Flauta", "Clarinete", "Saxofón", "Trompeta", "Trombón",
                "Percusión", "Canto", "Otro"
            ],
            width=38
        )
        instrumento_combo.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        row += 1
        
        # Nivel
        ttk.Label(scrollable_frame, text="Nivel:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.nivel_var = tk.StringVar()
        nivel_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.nivel_var,
            values=["Inicial", "Intermedio", "Avanzado"],
            width=38,
            state="readonly"
        )
        nivel_combo.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        row += 1
        
        # Experiencia previa
        ttk.Label(scrollable_frame, text="Experiencia Previa:").grid(
            row=row, column=0, sticky="nw", padx=10, pady=5
        )
        self.experiencia_var = tk.StringVar()
        experiencia_text = tk.Text(scrollable_frame, height=4, width=30)
        experiencia_text.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        self.experiencia_text = experiencia_text
        row += 1
        
        # Status and Notes Section
        ttk.Label(
            scrollable_frame,
            text="Estado y Notas",
            font=("Arial", 12, "bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 5))
        row += 1
        
        ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5
        )
        row += 1
        
        # Estado
        ttk.Label(scrollable_frame, text="Estado:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.estado_var = tk.StringVar(value="Pendiente")
        estado_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.estado_var,
            values=["Pendiente", "Aprobado", "Rechazado"],
            width=38,
            state="readonly"
        )
        estado_combo.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        row += 1
        
        # Notas
        ttk.Label(scrollable_frame, text="Notas:").grid(row=row, column=0, sticky="nw", padx=10, pady=5)
        self.notas_text = tk.Text(scrollable_frame, height=4, width=30)
        self.notas_text.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Guardar", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def populate_fields(self):
        """Populate form fields with student data."""
        if not self.student:
            return
        
        self.nombre_var.set(self.student.nombre)
        self.apellido_var.set(self.student.apellido)
        self.dni_var.set(self.student.dni)
        self.fecha_nac_var.set(self.student.fecha_nacimiento)
        self.email_var.set(self.student.email)
        self.telefono_var.set(self.student.telefono)
        self.direccion_var.set(self.student.direccion)
        self.ciudad_var.set(self.student.ciudad)
        self.provincia_var.set(self.student.provincia)
        self.codigo_postal_var.set(self.student.codigo_postal)
        self.contacto_nombre_var.set(self.student.contacto_emergencia_nombre)
        self.contacto_telefono_var.set(self.student.contacto_emergencia_telefono)
        self.contacto_relacion_var.set(self.student.contacto_emergencia_relacion)
        self.instrumento_var.set(self.student.instrumento)
        self.nivel_var.set(self.student.nivel)
        self.experiencia_text.insert("1.0", self.student.experiencia_previa)
        self.estado_var.set(self.student.estado)
        self.notas_text.insert("1.0", self.student.notas)
    
    def validate_form(self) -> bool:
        """Validate form data."""
        # Required fields
        if not self.nombre_var.get().strip():
            messagebox.showerror("Error", "El nombre es requerido.")
            return False
        
        if not self.apellido_var.get().strip():
            messagebox.showerror("Error", "El apellido es requerido.")
            return False
        
        # Validate DNI
        dni = self.dni_var.get().strip()
        if not validate_dni(dni):
            messagebox.showerror("Error", "El DNI debe tener 7-8 dígitos.")
            return False
        
        # Check if DNI exists (only for new students)
        if not self.student:
            existing = self.db.get_student_by_dni(dni)
            if existing:
                messagebox.showerror("Error", "Ya existe un estudiante con este DNI.")
                return False
        
        # Validate fecha de nacimiento
        if not self.fecha_nac_var.get().strip():
            messagebox.showerror("Error", "La fecha de nacimiento es requerida.")
            return False
        
        # Validate email
        email = self.email_var.get().strip()
        if not validate_email(email):
            messagebox.showerror("Error", "El email no es válido.")
            return False
        
        # Validate phone
        telefono = self.telefono_var.get().strip()
        if not validate_phone(telefono):
            messagebox.showerror("Error", "El teléfono debe tener al menos 8 dígitos.")
            return False
        
        # Validate address
        if not self.direccion_var.get().strip():
            messagebox.showerror("Error", "La dirección es requerida.")
            return False
        
        return True
    
    def save(self):
        """Save student data."""
        if not self.validate_form():
            return
        
        try:
            # Create or update student
            if self.student:
                # Update existing student
                self.student.nombre = self.nombre_var.get().strip()
                self.student.apellido = self.apellido_var.get().strip()
                self.student.dni = self.dni_var.get().strip()
                self.student.fecha_nacimiento = self.fecha_nac_var.get().strip()
                self.student.email = self.email_var.get().strip()
                self.student.telefono = self.telefono_var.get().strip()
                self.student.direccion = self.direccion_var.get().strip()
                self.student.ciudad = self.ciudad_var.get().strip()
                self.student.provincia = self.provincia_var.get().strip()
                self.student.codigo_postal = self.codigo_postal_var.get().strip()
                self.student.contacto_emergencia_nombre = self.contacto_nombre_var.get().strip()
                self.student.contacto_emergencia_telefono = self.contacto_telefono_var.get().strip()
                self.student.contacto_emergencia_relacion = self.contacto_relacion_var.get().strip()
                self.student.instrumento = self.instrumento_var.get().strip()
                self.student.nivel = self.nivel_var.get().strip()
                self.student.experiencia_previa = self.experiencia_text.get("1.0", tk.END).strip()
                self.student.estado = self.estado_var.get()
                self.student.notas = self.notas_text.get("1.0", tk.END).strip()
                
                self.db.update_student(self.student)
                messagebox.showinfo("Éxito", "Estudiante actualizado correctamente.")
            else:
                # Create new student
                student = Student(
                    nombre=self.nombre_var.get().strip(),
                    apellido=self.apellido_var.get().strip(),
                    dni=self.dni_var.get().strip(),
                    fecha_nacimiento=self.fecha_nac_var.get().strip(),
                    email=self.email_var.get().strip(),
                    telefono=self.telefono_var.get().strip(),
                    direccion=self.direccion_var.get().strip(),
                    ciudad=self.ciudad_var.get().strip(),
                    provincia=self.provincia_var.get().strip(),
                    codigo_postal=self.codigo_postal_var.get().strip(),
                    contacto_emergencia_nombre=self.contacto_nombre_var.get().strip(),
                    contacto_emergencia_telefono=self.contacto_telefono_var.get().strip(),
                    contacto_emergencia_relacion=self.contacto_relacion_var.get().strip(),
                    instrumento=self.instrumento_var.get().strip(),
                    nivel=self.nivel_var.get().strip(),
                    experiencia_previa=self.experiencia_text.get("1.0", tk.END).strip(),
                    estado=self.estado_var.get(),
                    notas=self.notas_text.get("1.0", tk.END).strip()
                )
                
                self.db.add_student(student)
                messagebox.showinfo("Éxito", "Estudiante registrado correctamente.")
            
            # Call callback
            if self.on_save:
                self.on_save()
            
            # Close window
            self.window.destroy()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar estudiante: {str(e)}")
