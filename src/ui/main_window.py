"""Main window for the application."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
from ..models import Student, Database
from ..export import PDFExporter, ExcelExporter
from ..email import EmailSender
from ..sync import GoogleSheetsSync
from ..config import Config
from ..utils import validate_dni, validate_email, validate_phone
from .student_form import StudentForm
from .student_list import StudentList


class MainWindow:
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        self.root = tk.Tk()
        self.root.title(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        self.root.geometry("1200x800")
        
        # Initialize components
        Config.ensure_directories()
        self.db = Database()
        self.pdf_exporter = PDFExporter()
        self.excel_exporter = ExcelExporter()
        self.email_sender = EmailSender()
        self.sheets_sync = GoogleSheetsSync()
        
        # Selected student
        self.selected_student: Optional[Student] = None
        
        # Create UI
        self.create_menu()
        self.create_main_layout()
        
        # Load initial data
        self.refresh_student_list()
    
    def create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Exportar a PDF", command=self.export_to_pdf)
        file_menu.add_command(label="Exportar a Excel", command=self.export_to_excel)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Students menu
        students_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Estudiantes", menu=students_menu)
        students_menu.add_command(label="Nuevo Estudiante", command=self.new_student)
        students_menu.add_command(label="Editar Estudiante", command=self.edit_student)
        students_menu.add_command(label="Eliminar Estudiante", command=self.delete_student)
        students_menu.add_separator()
        students_menu.add_command(label="Actualizar Lista", command=self.refresh_student_list)
        
        # Email menu
        email_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Email", menu=email_menu)
        email_menu.add_command(label="Enviar Bienvenida", command=self.send_welcome_email)
        email_menu.add_command(label="Enviar Certificado", command=self.send_certificate_email)
        email_menu.add_command(label="Enviar Actualización de Estado", command=self.send_status_update)
        
        # Sync menu
        sync_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sincronización", menu=sync_menu)
        sync_menu.add_command(label="Sincronizar con Google Sheets", command=self.sync_to_sheets)
        sync_menu.add_command(label="Importar desde Google Sheets", command=self.import_from_sheets)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.show_about)
    
    def create_main_layout(self):
        """Create main layout."""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Student list
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Search frame
        search_frame = ttk.Frame(left_panel)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_students())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Filter by status
        ttk.Label(search_frame, text="Estado:").pack(side=tk.LEFT, padx=(10, 5))
        self.status_filter = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(
            search_frame,
            textvariable=self.status_filter,
            values=["Todos", "Pendiente", "Aprobado", "Rechazado"],
            state="readonly",
            width=15
        )
        status_combo.pack(side=tk.LEFT)
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_by_status())
        
        # Student list
        self.student_list = StudentList(left_panel, self.on_student_selected)
        self.student_list.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Actions
        right_panel = ttk.Frame(main_container, width=250)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Title
        title_label = ttk.Label(
            right_panel,
            text="Acciones",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Buttons
        btn_width = 20
        
        ttk.Button(
            right_panel,
            text="Nuevo Estudiante",
            command=self.new_student,
            width=btn_width
        ).pack(pady=5)
        
        ttk.Button(
            right_panel,
            text="Editar Estudiante",
            command=self.edit_student,
            width=btn_width
        ).pack(pady=5)
        
        ttk.Button(
            right_panel,
            text="Eliminar Estudiante",
            command=self.delete_student,
            width=btn_width
        ).pack(pady=5)
        
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        ttk.Button(
            right_panel,
            text="Ver Detalles",
            command=self.view_details,
            width=btn_width
        ).pack(pady=5)
        
        ttk.Button(
            right_panel,
            text="Generar Certificado",
            command=self.generate_certificate,
            width=btn_width
        ).pack(pady=5)
        
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        ttk.Button(
            right_panel,
            text="Exportar Lista (PDF)",
            command=self.export_to_pdf,
            width=btn_width
        ).pack(pady=5)
        
        ttk.Button(
            right_panel,
            text="Exportar Lista (Excel)",
            command=self.export_to_excel,
            width=btn_width
        ).pack(pady=5)
        
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        ttk.Button(
            right_panel,
            text="Sincronizar Sheets",
            command=self.sync_to_sheets,
            width=btn_width
        ).pack(pady=5)
        
        # Status bar
        self.status_bar = ttk.Label(
            self.root,
            text="Listo",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def on_student_selected(self, student: Optional[Student]):
        """Handle student selection."""
        self.selected_student = student
        if student:
            self.status_bar.config(text=f"Seleccionado: {student.get_full_name()} - DNI: {student.dni}")
        else:
            self.status_bar.config(text="Listo")
    
    def refresh_student_list(self):
        """Refresh the student list."""
        students = self.db.get_all_students()
        self.student_list.update_students(students)
        self.status_bar.config(text=f"Lista actualizada - Total: {len(students)} estudiantes")
    
    def search_students(self):
        """Search students by query."""
        query = self.search_var.get().strip()
        if query:
            students = self.db.search_students(query)
        else:
            students = self.db.get_all_students()
        
        # Apply status filter
        status = self.status_filter.get()
        if status != "Todos":
            students = [s for s in students if s.estado == status]
        
        self.student_list.update_students(students)
    
    def filter_by_status(self):
        """Filter students by status."""
        self.search_students()
    
    def new_student(self):
        """Open form to create new student."""
        form = StudentForm(self.root, self.db, on_save=self.refresh_student_list)
    
    def edit_student(self):
        """Open form to edit selected student."""
        if not self.selected_student:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un estudiante para editar.")
            return
        
        form = StudentForm(
            self.root,
            self.db,
            student=self.selected_student,
            on_save=self.refresh_student_list
        )
    
    def delete_student(self):
        """Delete selected student."""
        if not self.selected_student:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un estudiante para eliminar.")
            return
        
        response = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar a {self.selected_student.get_full_name()}?"
        )
        
        if response:
            self.db.delete_student(self.selected_student.id)
            messagebox.showinfo("Éxito", "Estudiante eliminado correctamente.")
            self.refresh_student_list()
    
    def view_details(self):
        """View detailed information of selected student."""
        if not self.selected_student:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un estudiante.")
            return
        
        # Create detail window
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Detalles - {self.selected_student.get_full_name()}")
        detail_window.geometry("600x700")
        
        # Create scrollable frame
        canvas = tk.Canvas(detail_window)
        scrollbar = ttk.Scrollbar(detail_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add student details
        details = [
            ("Nombre completo", self.selected_student.get_full_name()),
            ("DNI", self.selected_student.dni),
            ("Fecha de nacimiento", self.selected_student.fecha_nacimiento),
            ("Email", self.selected_student.email),
            ("Teléfono", self.selected_student.telefono),
            ("Dirección", self.selected_student.direccion),
            ("Ciudad", self.selected_student.ciudad),
            ("Provincia", self.selected_student.provincia),
            ("Código Postal", self.selected_student.codigo_postal or '-'),
            ("", ""),
            ("Contacto de emergencia", self.selected_student.contacto_emergencia_nombre or '-'),
            ("Teléfono de emergencia", self.selected_student.contacto_emergencia_telefono or '-'),
            ("Relación", self.selected_student.contacto_emergencia_relacion or '-'),
            ("", ""),
            ("Instrumento", self.selected_student.instrumento or '-'),
            ("Nivel", self.selected_student.nivel or '-'),
            ("Experiencia previa", self.selected_student.experiencia_previa or '-'),
            ("", ""),
            ("Fecha de inscripción", self.selected_student.fecha_inscripcion),
            ("Estado", self.selected_student.estado),
            ("Notas", self.selected_student.notas or '-'),
        ]
        
        for i, (label, value) in enumerate(details):
            if label == "":
                ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).grid(
                    row=i, column=0, columnspan=2, sticky="ew", pady=10
                )
            else:
                ttk.Label(
                    scrollable_frame,
                    text=f"{label}:",
                    font=("Arial", 10, "bold")
                ).grid(row=i, column=0, sticky="w", padx=10, pady=5)
                
                ttk.Label(
                    scrollable_frame,
                    text=str(value),
                    wraplength=350
                ).grid(row=i, column=1, sticky="w", padx=10, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def generate_certificate(self):
        """Generate certificate for selected student."""
        if not self.selected_student:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un estudiante.")
            return
        
        try:
            filepath = self.pdf_exporter.generate_certificate(self.selected_student)
            messagebox.showinfo(
                "Éxito",
                f"Certificado generado correctamente:\n{filepath}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar certificado: {str(e)}")
    
    def export_to_pdf(self):
        """Export student list to PDF."""
        students = self.db.get_all_students()
        if not students:
            messagebox.showwarning("Advertencia", "No hay estudiantes para exportar.")
            return
        
        try:
            filepath = self.pdf_exporter.export_student_list(students)
            messagebox.showinfo(
                "Éxito",
                f"Lista exportada a PDF correctamente:\n{filepath}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar PDF: {str(e)}")
    
    def export_to_excel(self):
        """Export student list to Excel."""
        students = self.db.get_all_students()
        if not students:
            messagebox.showwarning("Advertencia", "No hay estudiantes para exportar.")
            return
        
        try:
            filepath = self.excel_exporter.export_student_list(students)
            messagebox.showinfo(
                "Éxito",
                f"Lista exportada a Excel correctamente:\n{filepath}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar Excel: {str(e)}")
    
    def send_welcome_email(self):
        """Send welcome email to selected student."""
        if not self.selected_student:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un estudiante.")
            return
        
        try:
            success = self.email_sender.send_welcome_email(self.selected_student)
            if success:
                messagebox.showinfo("Éxito", "Email de bienvenida enviado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo enviar el email. Verifica la configuración.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar email: {str(e)}")
    
    def send_certificate_email(self):
        """Send certificate email to selected student."""
        if not self.selected_student:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un estudiante.")
            return
        
        try:
            # Generate certificate
            cert_path = self.pdf_exporter.generate_certificate(self.selected_student)
            
            # Send email
            success = self.email_sender.send_certificate(self.selected_student, cert_path)
            if success:
                messagebox.showinfo("Éxito", "Certificado enviado por email correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo enviar el email. Verifica la configuración.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar certificado: {str(e)}")
    
    def send_status_update(self):
        """Send status update email to selected student."""
        if not self.selected_student:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un estudiante.")
            return
        
        try:
            success = self.email_sender.send_status_update(self.selected_student)
            if success:
                messagebox.showinfo("Éxito", "Email de actualización enviado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo enviar el email. Verifica la configuración.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar email: {str(e)}")
    
    def sync_to_sheets(self):
        """Sync students to Google Sheets."""
        students = self.db.get_all_students()
        if not students:
            messagebox.showwarning("Advertencia", "No hay estudiantes para sincronizar.")
            return
        
        try:
            success = self.sheets_sync.sync_students(students)
            if success:
                messagebox.showinfo("Éxito", "Datos sincronizados con Google Sheets correctamente.")
            else:
                messagebox.showerror(
                    "Error",
                    "No se pudo sincronizar. Verifica las credenciales y la configuración."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error al sincronizar: {str(e)}")
    
    def import_from_sheets(self):
        """Import students from Google Sheets."""
        response = messagebox.askyesno(
            "Confirmar importación",
            "¿Deseas importar estudiantes desde Google Sheets?\n"
            "Esto puede sobrescribir datos existentes."
        )
        
        if not response:
            return
        
        try:
            students = self.sheets_sync.get_students_from_sheet()
            if students:
                for student in students:
                    existing = self.db.get_student_by_dni(student.dni)
                    if existing:
                        student.id = existing.id
                        self.db.update_student(student)
                    else:
                        self.db.add_student(student)
                
                self.refresh_student_list()
                messagebox.showinfo("Éxito", f"Se importaron {len(students)} estudiantes.")
            else:
                messagebox.showwarning("Advertencia", "No se encontraron estudiantes en la hoja.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar: {str(e)}")
    
    def show_about(self):
        """Show about dialog."""
        about_text = f"""{Config.APP_NAME}
Versión {Config.APP_VERSION}

Sistema de gestión de inscripciones para:
{Config.SCHOOL_NAME}
{Config.PROGRAM_NAME}

Características:
• Gestión de estudiantes
• Exportación a PDF/Excel
• Envío de emails con certificados
• Sincronización con Google Sheets
"""
        messagebox.showinfo("Acerca de", about_text)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()
