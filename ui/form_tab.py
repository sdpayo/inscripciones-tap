"""Pestaña de Formulario de Inscripción."""
import sys
import os
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog
from services.pdf_generator import generar_certificado_pdf
from services.email_service import send_certificado_via_email, get_smtp_config
from config.settings import CERTIFICATES_DIR
from tkinter import ttk, messagebox
from datetime import datetime
from ui.base_tab import BaseTab
from database.csv_handler import (
    cargar_registros, guardar_registro, 
    actualizar_registro, eliminar_registro,
    generar_id
)
from models.materias import (
    get_todas_materias,
    get_materias_por_anio,
    get_profesores_materia,
    get_comisiones_profesor,
    get_horario
)
from services.validators import (
    validar_dni, validar_email, validar_telefono,
    validar_edad_minima, validar_datos_inscripcion
)
from services.pdf_generator import generar_certificado_pdf
from config.settings import settings

# Detectar pandas
try:
    import pandas as pd
    _HAS_PANDAS = True
except ImportError:
    _HAS_PANDAS = False


class FormTab(BaseTab):
    """Pestaña de formulario de inscripción."""
                
    def _build_ui(self):
        """Construye la interfaz del formulario con layout de 2 columnas."""
        # Contenedor principal con dos paneles
        main_paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
    
        # === PANEL IZQUIERDO: FORMULARIO ===
        left_panel = ttk.Frame(main_paned)
        main_paned.add(left_panel, weight=1)
    
        # Contenedor con scroll para el formulario
        canvas = tk.Canvas(left_panel)
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=canvas.yview)
        self.form_container = ttk.Frame(canvas)
    
        self.form_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
    
        canvas.create_window((0, 0), window=self.form_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
    
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
        # Construir secciones del formulario
        self._build_datos_personales()
        self._build_datos_contacto()
        self._build_datos_responsables()
        self._build_otros_datos()
        self._build_inscripcion()
        self._build_buttons()
    
        # === PANEL DERECHO: TABLA ===
        right_panel = ttk.Frame(main_paned)
        main_paned.add(right_panel, weight=1)
    
        # Llamar al método _build_table que ya existe
        # Este método construye todo: título, buscador, tabla y botones
        self._build_table(right_panel)

    def _build_form(self, parent):
        """Construye el formulario de inscripción."""
        # Canvas con scrollbar para formulario largo
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        ttk.Label(
            scrollable_frame,
            text="Nueva Inscripción",
            font=("Helvetica", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        row = 1
        
        # ========== DATOS PERSONALES ==========
        ttk.Label(
            scrollable_frame,
            text="Datos Personales",
            font=("Helvetica", 11, "bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 5))
        row += 1
        
        ttk.Separator(scrollable_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=5
        )
        row += 1
        
        # Nombre
        ttk.Label(scrollable_frame, text="Nombre:*").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.nombre_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.nombre_var, width=30).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        row += 1
        
        # Apellido
        ttk.Label(scrollable_frame, text="Apellido:*").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.apellido_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.apellido_var, width=30).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        row += 1
        
        # DNI
        ttk.Label(scrollable_frame, text="DNI:*").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.dni_var = tk.StringVar()
        dni_entry = ttk.Entry(scrollable_frame, textvariable=self.dni_var, width=15)
        dni_entry.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        dni_entry.bind("<FocusOut>", self._validar_dni)
        row += 1
        
        # Edad
        ttk.Label(scrollable_frame, text="Edad:*").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.edad_var = tk.IntVar(value=0)
        ttk.Spinbox(scrollable_frame, textvariable=self.edad_var, from_=0, to=99, width=8).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        row += 1
        
        # Legajo
        ttk.Label(scrollable_frame, text="Legajo:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.legajo_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.legajo_var, width=15).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        row += 1
        
        # Email
        ttk.Label(scrollable_frame, text="Email:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(scrollable_frame, textvariable=self.email_var, width=35)
        email_entry.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        email_entry.bind("<FocusOut>", self._validar_email)
        row += 1
        
        # Teléfono
        ttk.Label(scrollable_frame, text="Teléfono:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.telefono_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.telefono_var, width=20).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        row += 1
        
        # Domicilio
        ttk.Label(scrollable_frame, text="Domicilio:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.domicilio_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.domicilio_var, width=35).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        row += 1
        
        # ========== DATOS FAMILIARES ==========
        ttk.Label(
            scrollable_frame,
            text="Datos Familiares",
            font=("Helvetica", 11, "bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(15, 5))
        row += 1
        
        ttk.Separator(scrollable_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=5
        )
        row += 1
        
        # Nombre Padre
        ttk.Label(scrollable_frame, text="Nombre Padre:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.nombre_padre_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.nombre_padre_var, width=30).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        row += 1
        
        # Nombre Madre
        ttk.Label(scrollable_frame, text="Nombre Madre:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.nombre_madre_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.nombre_madre_var, width=30).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        row += 1
        
        # Contacto Tutor
        ttk.Label(scrollable_frame, text="Contacto Tutor:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.contacto_tutor_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.contacto_tutor_var, width=25).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        row += 1
        
        # ========== DATOS ACADÉMICOS ==========
        ttk.Label(
            scrollable_frame,
            text="Datos Académicos",
            font=("Helvetica", 11, "bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(15, 5))
        row += 1
        
        ttk.Separator(scrollable_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=5
        )
        row += 1
        
        # Turno
        ttk.Label(scrollable_frame, text="Turno:*").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.turno_var = tk.StringVar()
        ttk.Combobox(
            scrollable_frame,
            textvariable=self.turno_var,
            values=["Mañana", "Tarde", "Vespertino"],
            state="readonly",
            width=15
        ).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        # Año
        ttk.Label(scrollable_frame, text="Año:*").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.anio_var = tk.IntVar(value=1)
        ttk.Combobox(
            scrollable_frame,
            textvariable=self.anio_var,
            values=[1, 2, 3, 4],
            state="readonly",
            width=8
        ).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        # Materia
        ttk.Label(scrollable_frame, text="Materia:*").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.materia_var = tk.StringVar()
        self.materia_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.materia_var,
            values=get_todas_materias(),
            state="readonly",
            width=30
        )
        self.materia_combo.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        self.materia_combo.bind("<<ComboboxSelected>>", self._on_materia_change)
        row += 1
        
        # Profesor
        ttk.Label(scrollable_frame, text="Profesor:*").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.profesor_var = tk.StringVar()
        self.profesor_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.profesor_var,
            values=[],
            state="readonly",
            width=30
        )
        self.profesor_combo.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        self.profesor_combo.bind("<<ComboboxSelected>>", self._on_profesor_change)
        row += 1
        
        # Comisión
        ttk.Label(scrollable_frame, text="Comisión:*").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.comision_var = tk.StringVar()
        self.comision_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.comision_var,
            values=[],
            state="readonly",
            width=15
        )
        self.comision_combo.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        # Horario
        ttk.Label(scrollable_frame, text="Horario:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.horario_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.horario_var, width=25).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        row += 1
        
        # ========== OTROS DATOS ==========
        ttk.Label(
            scrollable_frame,
            text="Otros Datos",
            font=("Helvetica", 11, "bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(15, 5))
        row += 1
        
        ttk.Separator(scrollable_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=5
        )
        row += 1
        
        # SAETA
        ttk.Label(scrollable_frame, text="SAETA:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.saeta_var = tk.StringVar(value="No")
        ttk.Combobox(
            scrollable_frame,
            textvariable=self.saeta_var,
            values=["Sí", "No"],
            state="readonly",
            width=10
        ).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        # Obra Social
        ttk.Label(scrollable_frame, text="Obra Social:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.obra_social_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.obra_social_var, width=25).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        row += 1
        
        # Seguro Escolar
        ttk.Label(scrollable_frame, text="Seguro Escolar:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.seguro_escolar_var = tk.StringVar(value="No")
        ttk.Combobox(
            scrollable_frame,
            textvariable=self.seguro_escolar_var,
            values=["Sí", "No"],
            state="readonly",
            width=10
        ).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        # Pago Voluntario
        ttk.Label(scrollable_frame, text="Pago Voluntario:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.pago_voluntario_var = tk.StringVar(value="No")
        ttk.Combobox(
            scrollable_frame,
            textvariable=self.pago_voluntario_var,
            values=["Sí", "No"],
            state="readonly",
            width=10
        ).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        # Monto
        ttk.Label(scrollable_frame, text="Monto:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.monto_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.monto_var, width=15).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        row += 1
        
        # Permiso
        ttk.Label(scrollable_frame, text="Permiso:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.permiso_var = tk.StringVar(value="No")
        ttk.Combobox(
            scrollable_frame,
            textvariable=self.permiso_var,
            values=["Sí", "No"],
            state="readonly",
            width=10
        ).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        # Observaciones
        ttk.Label(scrollable_frame, text="Observaciones:").grid(
            row=row, column=0, sticky="ne", padx=5, pady=3
        )
        self.observaciones_text = tk.Text(scrollable_frame, width=30, height=3)
        self.observaciones_text.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        # ========== BOTONES ==========
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        self.guardar_btn = ttk.Button(
            btn_frame,
            text="💾 Guardar",
            command=self._guardar_inscripcion
        )
        self.guardar_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="🗑️ Limpiar",
            command=self._limpiar_formulario
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            scrollable_frame,
            text="* Campos obligatorios",
            foreground="gray",
            font=("Helvetica", 8)
        ).grid(row=row+1, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Variable para modo edición
        self.editing_id = None
    
    def _build_table(self, parent):
        """Construye tabla de inscripciones registradas."""
        # Contenedor principal
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # === HEADER ===
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(
            header_frame,
            text="Inscripciones Registradas",
            font=("Helvetica", 12, "bold")
        ).pack(side=tk.LEFT)
        
        # Buscador
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._filtrar_tabla())
        ttk.Entry(search_frame, textvariable=self.search_var, width=25).pack(side=tk.LEFT)
        
        # === TABLA ===
        table_frame = ttk.Frame(container)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        tree_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview
        columns = ("ID", "Nombre", "Apellido", "DNI", "Materia", "Profesor", "Turno", "Año")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            height=15
        )
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Configurar columnas
        column_widths = {
            "ID": 80,
            "Nombre": 120,
            "Apellido": 120,
            "DNI": 100,
            "Materia": 200,
            "Profesor": 150,
            "Turno": 80,
            "Año": 50
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col], anchor="w")
        
        # Pack
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        # === BOTONES ===
        buttons_frame = ttk.Frame(container)
        buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            buttons_frame,
            text="✏️ Editar",
            command=self._editar_seleccionado
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            buttons_frame,
            text="🗑️ Eliminar",
            command=self._eliminar_seleccionado
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            buttons_frame,
            text="📄 Certificado",
            command=self._generar_certificado_seleccionado
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            buttons_frame,
            text="🔄 Refrescar",
            command=self.refresh
        ).pack(side=tk.RIGHT, padx=2)
        
        # Cargar datos iniciales
        self.refresh()

    def _show_context_menu(self, event):
        """Muestra menú contextual."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    # ========== VALIDACIONES ==========
    
    def _validar_dni(self, event=None):
        """Valida DNI en tiempo real."""
        dni = self.dni_var.get().strip()
        if dni and not validar_dni(dni):
            self.show_warning("DNI", "El DNI debe tener 7-8 dígitos.")
    
    def _validar_email(self, event=None):
        """Valida email en tiempo real."""
        email = self.email_var.get().strip()
        if email and not validar_email(email):
            self.show_warning("Email", "El formato del email no es válido.")
    
    # ========== CASCADA MATERIA/PROFESOR/COMISION ==========
    
    def _on_materia_change(self, event=None):
        """Actualiza profesores al cambiar materia."""
        materia = self.materia_var.get()
        if not materia:
            return
        
        profesores = get_profesores_materia(materia)
        self.profesor_combo['values'] = profesores
        
        if profesores:
            self.profesor_var.set(profesores[0])
            self._on_profesor_change()
        else:
            self.profesor_var.set("")
            self.comision_combo['values'] = []
            self.comision_var.set("")
    
    def _on_profesor_change(self, event=None):
        """Actualiza comisiones al cambiar profesor."""
        materia = self.materia_var.get()
        profesor = self.profesor_var.get()
        
        if not materia or not profesor:
            return
        
        comisiones = get_comisiones_materia(materia, profesor)
        self.comision_combo['values'] = comisiones
        
        if comisiones:
            self.comision_var.set(comisiones[0])
        else:
            self.comision_var.set("")
    
    # ========== GUARDAR/EDITAR ==========
    
    def _guardar_inscripcion(self):
        """Guarda o actualiza inscripción."""
        # Recolectar datos
        datos = {
            "nombre": self.nombre_var.get().strip(),
            "apellido": self.apellido_var.get().strip(),
            "dni": self.dni_var.get().strip(),
            "edad": self.edad_var.get(),
            "legajo": self.legajo_var.get().strip(),
            "email": self.email_var.get().strip(),
            "telefono": self.telefono_var.get().strip(),
            "domicilio": self.domicilio_var.get().strip(),
            "nombre_padre": self.nombre_padre_var.get().strip(),
            "nombre_madre": self.nombre_madre_var.get().strip(),
            "contacto_tutor": self.contacto_tutor_var.get().strip(),
            "turno": self.turno_var.get(),
            "anio": self.anio_var.get(),
            "materia": self.materia_var.get(),
            "profesor": self.profesor_var.get(),
            "comision": self.comision_var.get(),
            "horario": self.horario_var.get().strip(),
            "saeta": self.saeta_var.get(),
            "obra_social": self.obra_social_var.get().strip(),
            "seguro_escolar": self.seguro_escolar_var.get(),
            "pago_voluntario": self.pago_voluntario_var.get(),
            "monto": self.monto_var.get().strip(),
            "permiso": self.permiso_var.get(),
            "observaciones": self.observaciones_text.get("1.0", tk.END).strip(),
            "en_lista_espera": "No"
        }
        
        # Validar
        ok, msg = validar_datos_inscripcion(datos)
        if not ok:
            self.show_error("Validación", msg)
            return
        
        # Guardar
        try:
            if self.editing_id:
                # Actualizar existente
                datos["id"] = self.editing_id
                datos["fecha_inscripcion"] = self._get_fecha_inscripcion(self.editing_id)
                actualizar_registro(datos)
                self.show_info("Éxito", f"Inscripción actualizada: {datos['nombre']} {datos['apellido']}")
                self.editing_id = None
                self.guardar_btn.config(text="💾 Guardar")
            else:
                # Nueva inscripción
                datos["id"] = generar_id()
                datos["fecha_inscripcion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                guardar_registro(datos)
                self.show_info("Éxito", f"Inscripción guardada: {datos['nombre']} {datos['apellido']}")
            
            # Limpiar y refrescar
            self._limpiar_formulario()
            self.refresh()
            
        except Exception as e:
            self.show_error("Error", f"No se pudo guardar: {e}")
    
    def _get_fecha_inscripcion(self, reg_id):
        """Obtiene fecha original de inscripción."""
        registros = cargar_registros()
        for reg in registros:
            if reg.get("id") == reg_id:
                return reg.get("fecha_inscripcion", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        self.nombre_var.set("")
        self.apellido_var.set("")
        self.dni_var.set("")
        self.edad_var.set(0)
        self.legajo_var.set("")
        self.email_var.set("")
        self.telefono_var.set("")
        self.domicilio_var.set("")
        self.nombre_padre_var.set("")
        self.nombre_madre_var.set("")
        self.contacto_tutor_var.set("")
        self.turno_var.set("")
        self.anio_var.set(1)
        self.materia_var.set("")
        self.profesor_var.set("")
        self.comision_var.set("")
        self.horario_var.set("")
        self.saeta_var.set("No")
        self.obra_social_var.set("")
        self.seguro_escolar_var.set("No")
        self.pago_voluntario_var.set("No")
        self.monto_var.set("")
        self.permiso_var.set("No")
        self.observaciones_text.delete("1.0", tk.END)
        
        self.editing_id = None
        self.guardar_btn.config(text="💾 Guardar")
    
    # ========== ACCIONES TABLA ==========
    
    def _editar_seleccion(self, event):
        """Carga datos seleccionados en el formulario para editar."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Editar", "Seleccioná un registro para editar.")
            return
        
        item = self.tree.item(selection[0])
        reg_id = item["text"]
        
        # Buscar registro
        registros = cargar_registros()
        registro = None
        for reg in registros:
            if reg.get("id") == reg_id:
                registro = reg
                break
        
        if not registro:
            self.show_error("Error", "Registro no encontrado.")
            return
        
        # Cargar en formulario
        self.nombre_var.set(registro.get("nombre", ""))
        self.apellido_var.set(registro.get("apellido", ""))
        self.dni_var.set(registro.get("dni", ""))
        self.edad_var.set(registro.get("edad", 0))
        self.legajo_var.set(registro.get("legajo", ""))
        self.email_var.set(registro.get("mail", ""))
        self.telefono_var.set(registro.get("telefono", ""))
        self.domicilio_var.set(registro.get("domicilio", ""))
        self.nombre_padre_var.set(registro.get("nombre_padre", ""))
        self.nombre_madre_var.set(registro.get("nombre_madre", ""))
        self.contacto_tutor_var.set(registro.get("contacto_tutor", ""))
        self.turno_var.set(registro.get("turno", ""))
        self.anio_var.set(registro.get("anio", 1))
        self.materia_var.set(registro.get("materia", ""))
        self._on_materia_change()
        self.profesor_var.set(registro.get("profesor", ""))
        self._on_profesor_change()
        self.comision_var.set(registro.get("comision", ""))
        self.horario_var.set(registro.get("horario", ""))
        self.saeta_var.set(registro.get("saeta", "No"))
        self.obra_social_var.set(registro.get("obra_social", ""))
        self.seguro_escolar_var.set(registro.get("seguro_escolar", "No"))
        self.pago_voluntario_var.set(registro.get("pago_voluntario", "No"))
        self.monto_var.set(registro.get("monto", ""))
        self.permiso_var.set(registro.get("permiso", "No"))
        self.observaciones_text.delete("1.0", tk.END)
        self.observaciones_text.insert("1.0", registro.get("observaciones", ""))
        
        # Modo edición
        self.editing_id = reg_id
        self.guardar_btn.config(text="💾 Actualizar")
    
    def _eliminar_seleccion(self):
        """Elimina registro seleccionado."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Eliminar", "Seleccioná un registro para eliminar.")
            return
        
        item = self.tree.item(selection[0])
        reg_id = item["text"]
        nombre = item["values"][0]
        apellido = item["values"][1]
        
        if not self.ask_yes_no("Confirmar", f"¿Eliminar inscripción de {nombre} {apellido}?"):
            return
        
        try:
            eliminar_registro(reg_id)
            self.show_info("Éxito", "Inscripción eliminada.")
            self.refresh()
        except Exception as e:
            self.show_error("Error", f"No se pudo eliminar: {e}")
    
    def _generar_certificado_seleccion(self):
        """Genera certificado PDF para registro seleccionado."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Certificado", "Seleccioná un registro.")
            return
        
        item = self.tree.item(selection[0])
        reg_id = item["text"]
        
        # Buscar registro
        registros = cargar_registros()
        registro = None
        for reg in registros:
            if reg.get("id") == reg_id:
                registro = reg
                break
        
        if not registro:
            self.show_error("Error", "Registro no encontrado.")
            return
        
        # Validar seguro escolar si está configurado
        if settings.get("app.require_seguro_escolar"):
            if registro.get("seguro_escolar", "No") != "Sí":
                if not self.ask_yes_no(
                    "Seguro Escolar",
                    "El alumno no tiene seguro escolar. ¿Generar certificado de todos modos?"
                ):
                    return
        
        # Generar PDF
        try:
            ok, msg = generar_certificado_pdf(registro)
            if ok:
                self.show_info("Certificado", msg)
            else:
                self.show_error("Error", msg)
        except Exception as e:
            self.show_error("Error", f"No se pudo generar certificado: {e}")

    def _filtrar_tabla(self):
        """Filtra la tabla según el texto de búsqueda."""
        search_text = self.search_var.get().lower()
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Recargar registros filtrados
        from database.csv_handler import cargar_registros
        registros = cargar_registros()
        
        for reg in registros:
            # Filtrar por texto en nombre, apellido o DNI
            nombre = reg.get("nombre", "").lower()
            apellido = reg.get("apellido", "").lower()
            dni = reg.get("dni", "").lower()
            materia = reg.get("materia", "").lower()
            
            if (search_text in nombre or 
                search_text in apellido or 
                search_text in dni or
                search_text in materia):
                
                self.tree.insert("", tk.END, values=(
                    reg.get("id", "")[:8],
                    reg.get("nombre", ""),
                    reg.get("apellido", ""),
                    reg.get("dni", ""),
                    reg.get("materia", ""),
                    reg.get("profesor", ""),
                    reg.get("turno", ""),
                    reg.get("anio", "")
                ))

    def _editar_seleccionado(self):
        """Carga el registro seleccionado en el formulario para editar."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Editar", "Seleccioná un registro de la tabla")
            return
        
        # Obtener valores de la fila seleccionada
        item = self.tree.item(selection[0])
        values = item['values']
        
        if not values:
            return
        
        # Buscar registro completo por ID
        id_corto = values[0]
        from database.csv_handler import cargar_registros
        registros = cargar_registros()
        
        registro = None
        for reg in registros:
            if reg.get("id", "").startswith(id_corto):
                registro = reg
                break
        
        if not registro:
            self.show_error("Error", "No se encontró el registro completo")
            return
        
        # Cargar datos en el formulario
        self.nombre_var.set(registro.get("nombre", ""))
        self.apellido_var.set(registro.get("apellido", ""))
        self.dni_var.set(registro.get("dni", ""))
        self.fecha_nac_var.set(registro.get("fecha_nacimiento", ""))
        self.edad_var.set(registro.get("edad", ""))
        
        self.direccion_var.set(registro.get("direccion", ""))
        self.telefono_var.set(registro.get("telefono", ""))
        self.email_var.set(registro.get("email", ""))
        
        self.nombre_padre_var.set(registro.get("nombre_padre", ""))
        self.nombre_madre_var.set(registro.get("nombre_madre", ""))
        self.telefono_emergencia_var.set(registro.get("telefono_emergencia", ""))
        
        self.obra_social_var.set(registro.get("obra_social", ""))
        self.seguro_escolar_var.set(registro.get("seguro_escolar", "No"))
        
        self.anio_var.set(registro.get("anio", ""))
        self.turno_var.set(registro.get("turno", ""))
        self.materia_var.set(registro.get("materia", ""))
        self.profesor_var.set(registro.get("profesor", ""))
        self.comision_var.set(registro.get("comision", ""))
        self.horario_var.set(registro.get("horario", ""))
        
        self.observaciones_text.delete("1.0", tk.END)
        self.observaciones_text.insert("1.0", registro.get("observaciones", ""))
        
        self.show_info("Editar", "Registro cargado. Modificá los campos y guardá.")

    def _eliminar_seleccionado(self):
        """Elimina el registro seleccionado."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Eliminar", "Seleccioná un registro de la tabla")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        if not values:
            return
        
        nombre = values[1]
        apellido = values[2]
        
        if not self.ask_yes_no(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar la inscripción de {nombre} {apellido}?"
        ):
            return
        
        # Buscar y eliminar por ID
        id_corto = values[0]
        from database.csv_handler import cargar_registros, guardar_todos_registros
        registros = cargar_registros()
        
        registros_filtrados = [
            reg for reg in registros 
            if not reg.get("id", "").startswith(id_corto)
        ]
        
        ok, msg = guardar_todos_registros(registros_filtrados)
        
        if ok:
            self.show_info("Eliminado", "Registro eliminado correctamente")
            self.refresh()
            self.app.refresh_all()
        else:
            self.show_error("Error", msg)

    def _generar_certificado_seleccionado(self):
        """Genera certificado del registro seleccionado."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Certificado", "Seleccioná un registro de la tabla")
            return
        
        # Obtener ID y buscar registro completo
        item = self.tree.item(selection[0])
        values = item['values']
        id_corto = values[0]
        
        from database.csv_handler import cargar_registros
        registros = cargar_registros()
        
        registro = None
        for reg in registros:
            if reg.get("id", "").startswith(id_corto):
                registro = reg
                break
        
        if not registro:
            self.show_error("Error", "No se encontró el registro")
            return
        
        from services.pdf_generator import generar_certificado_pdf
        
        ok, msg = generar_certificado_pdf(registro)
        
        if ok:
            self.show_info("Certificado", msg)
        else:
            self.show_error("Error", msg)

    def _build_otros_datos(self):
        """Construye sección de Otros Datos."""
        otros_frame = ttk.LabelFrame(self.form_container, text="Otros Datos", padding=10)
        otros_frame.pack(fill=tk.X, padx=10, pady=10)
        
        row = 0
        
        # SAETA
        ttk.Label(otros_frame, text="SAETA:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.saeta_var = tk.StringVar()
        ttk.Combobox(
            otros_frame,
            textvariable=self.saeta_var,
            values=["No", "Sí"],
            state="readonly",
            width=15
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        self.saeta_var.set("No")
        
        # Obra Social
        ttk.Label(otros_frame, text="Obra Social:").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.obra_social_var = tk.StringVar()
        ttk.Entry(otros_frame, textvariable=self.obra_social_var, width=30).grid(
            row=row, column=3, sticky="w", padx=5, pady=5
        )
        row += 1
        
        # Seguro Escolar
        ttk.Label(otros_frame, text="Seguro Escolar:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.seguro_escolar_var = tk.StringVar()
        ttk.Combobox(
            otros_frame,
            textvariable=self.seguro_escolar_var,
            values=["No", "Sí"],
            state="readonly",
            width=15
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        self.seguro_escolar_var.set("No")
        
        # Pago Voluntario
        ttk.Label(otros_frame, text="Pago Voluntario:").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.pago_voluntario_var = tk.StringVar()
        ttk.Combobox(
            otros_frame,
            textvariable=self.pago_voluntario_var,
            values=["No", "Sí"],
            state="readonly",
            width=15
        ).grid(row=row, column=3, sticky="w", padx=5, pady=5)
        self.pago_voluntario_var.set("No")
        row += 1
        
        # Monto
        ttk.Label(otros_frame, text="Monto:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.monto_var = tk.StringVar()
        ttk.Entry(otros_frame, textvariable=self.monto_var, width=15).grid(
            row=row, column=1, sticky="w", padx=5, pady=5
        )
        
        # Permiso
        ttk.Label(otros_frame, text="Permiso:").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.permiso_var = tk.StringVar()
        ttk.Combobox(
            otros_frame,
            textvariable=self.permiso_var,
            values=["No", "Sí"],
            state="readonly",
            width=15
        ).grid(row=row, column=3, sticky="w", padx=5, pady=5)
        self.permiso_var.set("No")
        row += 1

    def _build_inscripcion(self):
        """Construye sección de Inscripción."""
        inscripcion_frame = ttk.LabelFrame(self.form_container, text="Inscripción", padding=10)
        inscripcion_frame.pack(fill=tk.X, padx=10, pady=10)
        
        row = 0
        
        # AÑO
        ttk.Label(inscripcion_frame, text="Año:*").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.anio_var = tk.StringVar()
        self.anio_combo = ttk.Combobox(
            inscripcion_frame,
            textvariable=self.anio_var,
            values=["1", "2", "3", "4"],
            state="readonly",
            width=10
        )
        self.anio_combo.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        self.anio_combo.bind("<<ComboboxSelected>>", self._on_anio_change)
        
        # TURNO
        ttk.Label(inscripcion_frame, text="Turno:*").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.turno_var = tk.StringVar()
        ttk.Combobox(
            inscripcion_frame,
            textvariable=self.turno_var,
            values=["Mañana", "Tarde", "Vespertino", "Noche"],
            state="readonly",
            width=15
        ).grid(row=row, column=3, sticky="w", padx=5, pady=5)
        row += 1
        
        # MATERIA
        ttk.Label(inscripcion_frame, text="Materia:*").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.materia_var = tk.StringVar()
        self.materia_combo = ttk.Combobox(
            inscripcion_frame,
            textvariable=self.materia_var,
            values=[],
            state="readonly",
            width=50
        )
        self.materia_combo.grid(row=row, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        self.materia_combo.bind("<<ComboboxSelected>>", self._on_materia_change)
        row += 1
        
        # PROFESOR/A
        ttk.Label(inscripcion_frame, text="Profesor/a:*").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.profesor_var = tk.StringVar()
        self.profesor_combo = ttk.Combobox(
            inscripcion_frame,
            textvariable=self.profesor_var,
            values=[],
            state="readonly",
            width=30
        )
        self.profesor_combo.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        self.profesor_combo.bind("<<ComboboxSelected>>", self._on_profesor_change)
        
        # COMISIÓN
        ttk.Label(inscripcion_frame, text="Comisión:*").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.comision_var = tk.StringVar()
        self.comision_combo = ttk.Combobox(
            inscripcion_frame,
            textvariable=self.comision_var,
            values=[],
            state="readonly",
            width=15
        )
        self.comision_combo.grid(row=row, column=3, sticky="w", padx=5, pady=5)
        self.comision_combo.bind("<<ComboboxSelected>>", self._on_comision_change)
        row += 1
        
        # HORARIO (automático)
        ttk.Label(inscripcion_frame, text="Horario:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.horario_var = tk.StringVar()
        ttk.Entry(
            inscripcion_frame,
            textvariable=self.horario_var,
            width=30,
            state="readonly"
        ).grid(row=row, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        row += 1  # ← ¡AGREGAR ESTA LÍNEA!
        
        # Texto informativo
        ttk.Label(
            inscripcion_frame,
            text="El horario se completa automáticamente",
            font=("Helvetica", 8),
            foreground="gray"
        ).grid(row=row, column=0, columnspan=4, sticky="w", padx=5)
        row += 1  # ← ¡AGREGAR ESTA LÍNEA!
        
        # OBSERVACIONES
        ttk.Label(inscripcion_frame, text="Observaciones:").grid(
            row=row, column=0, sticky="ne", padx=5, pady=5
        )
        self.observaciones_text = tk.Text(inscripcion_frame, width=60, height=3)
        self.observaciones_text.grid(
            row=row, column=1, columnspan=3, sticky="w", padx=5, pady=5
        )

    def _on_anio_change(self, event=None):
        """Al cambiar año, filtrar materias."""
        anio = self.anio_var.get()
        if not anio:
            return
        
        from models.materias import get_materias_por_anio
        materias = get_materias_por_anio(int(anio))
        self.materia_combo['values'] = materias
        self.materia_var.set("")
        self.profesor_var.set("")
        self.comision_var.set("")
        self.horario_var.set("")


    def _on_materia_change(self, event=None):
        """Al cambiar materia, cargar profesores."""
        materia = self.materia_var.get()
        if not materia:
            return
        
        from models.materias import get_profesores_materia
        profesores = get_profesores_materia(materia)
        self.profesor_combo['values'] = profesores
        self.profesor_var.set("")
        self.comision_var.set("")
        self.horario_var.set("")


    def _on_profesor_change(self, event=None):
        """Al cambiar profesor, cargar comisiones."""
        materia = self.materia_var.get()
        profesor = self.profesor_var.get()
        if not materia or not profesor:
            return
        
        from models.materias import get_comisiones_profesor
        comisiones = get_comisiones_profesor(materia, profesor)
        self.comision_combo['values'] = comisiones
        self.comision_var.set("")
        self.horario_var.set("")


    def _on_comision_change(self, event=None):
        """Al cambiar comisión, cargar horario."""
        materia = self.materia_var.get()
        profesor = self.profesor_var.get()
        comision = self.comision_var.get()
        if not all([materia, profesor, comision]):
            return
        
        from models.materias import get_horario
        horario = get_horario(materia, profesor, comision)
        self.horario_var.set(horario if horario else "Sin horario")

    def refresh(self):
        """Refresca la tabla con los registros guardados."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar registros desde CSV
        from database.csv_handler import cargar_registros
        registros = cargar_registros()
        
        # Poblar tabla
        for reg in registros:
            self.tree.insert("", tk.END, values=(
                reg.get("id", "")[:8],  # ID corto (primeros 8 caracteres)
                reg.get("nombre", ""),
                reg.get("apellido", ""),
                reg.get("dni", ""),
                reg.get("materia", ""),
                reg.get("profesor", ""),
                reg.get("turno", ""),
                reg.get("anio", "")
            ))


    # ========== REFRESCAR TABLA ==========
    

    def _build_datos_personales(self):
        """Construye sección de Datos Personales."""
        personales_frame = ttk.LabelFrame(self.form_container, text="Datos Personales", padding=10)
        personales_frame.pack(fill=tk.X, padx=10, pady=10)
        
        row = 0
        
        # Nombre
        ttk.Label(personales_frame, text="Nombre:*").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(personales_frame, textvariable=self.nombre_var, width=30).grid(
            row=row, column=1, sticky="w", padx=5, pady=5
        )
        
        # Apellido
        ttk.Label(personales_frame, text="Apellido:*").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.apellido_var = tk.StringVar()
        ttk.Entry(personales_frame, textvariable=self.apellido_var, width=30).grid(
            row=row, column=3, sticky="w", padx=5, pady=5
        )
        row += 1
        
        # DNI
        ttk.Label(personales_frame, text="DNI:*").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.dni_var = tk.StringVar()
        ttk.Entry(personales_frame, textvariable=self.dni_var, width=15).grid(
            row=row, column=1, sticky="w", padx=5, pady=5
        )
        
        # Fecha de Nacimiento
        ttk.Label(personales_frame, text="Fecha Nacimiento:").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.fecha_nac_var = tk.StringVar()
        ttk.Entry(personales_frame, textvariable=self.fecha_nac_var, width=15).grid(
            row=row, column=3, sticky="w", padx=5, pady=5
        )
        row += 1
        
        # Edad
        ttk.Label(personales_frame, text="Edad:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.edad_var = tk.StringVar()
        ttk.Entry(personales_frame, textvariable=self.edad_var, width=10).grid(
            row=row, column=1, sticky="w", padx=5, pady=5
        )

    def _build_datos_contacto(self):
        """Construye sección de Datos de Contacto."""
        contacto_frame = ttk.LabelFrame(self.form_container, text="Datos de Contacto", padding=10)
        contacto_frame.pack(fill=tk.X, padx=10, pady=10)
        
        row = 0
        
        # Dirección
        ttk.Label(contacto_frame, text="Dirección:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.direccion_var = tk.StringVar()
        ttk.Entry(contacto_frame, textvariable=self.direccion_var, width=50).grid(
            row=row, column=1, columnspan=3, sticky="w", padx=5, pady=5
        )
        row += 1
        
        # Teléfono
        ttk.Label(contacto_frame, text="Teléfono:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.telefono_var = tk.StringVar()
        ttk.Entry(contacto_frame, textvariable=self.telefono_var, width=20).grid(
            row=row, column=1, sticky="w", padx=5, pady=5
        )
        
        # Email
        ttk.Label(contacto_frame, text="Email:").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(contacto_frame, textvariable=self.email_var, width=30).grid(
            row=row, column=3, sticky="w", padx=5, pady=5
        )

    def _build_datos_responsables(self):
        """Construye sección de Datos de Responsables."""
        responsables_frame = ttk.LabelFrame(self.form_container, text="Datos de Responsables", padding=10)
        responsables_frame.pack(fill=tk.X, padx=10, pady=10)
        
        row = 0
        
        # Nombre Padre
        ttk.Label(responsables_frame, text="Nombre Padre:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.nombre_padre_var = tk.StringVar()
        ttk.Entry(responsables_frame, textvariable=self.nombre_padre_var, width=30).grid(
            row=row, column=1, sticky="w", padx=5, pady=5
        )
        
        # Nombre Madre
        ttk.Label(responsables_frame, text="Nombre Madre:").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.nombre_madre_var = tk.StringVar()
        ttk.Entry(responsables_frame, textvariable=self.nombre_madre_var, width=30).grid(
            row=row, column=3, sticky="w", padx=5, pady=5
        )
        row += 1
        
        # Teléfono Emergencia
        ttk.Label(responsables_frame, text="Tel. Emergencia:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.telefono_emergencia_var = tk.StringVar()
        ttk.Entry(responsables_frame, textvariable=self.telefono_emergencia_var, width=20).grid(
            row=row, column=1, sticky="w", padx=5, pady=5
        )

    def _build_buttons(self):
        """Construye sección de botones."""
        buttons_frame = ttk.Frame(self.form_container)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            buttons_frame,
            text="💾 Guardar Inscripción",
            command=self._guardar
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="🗑️ Limpiar Formulario",
            command=self._limpiar
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="📄 Generar Certificado",
            command=self._generar_certificado
        ).pack(side=tk.LEFT, padx=5)

    def _on_anio_change(self, event=None):
        """Filtrar materias por año."""
        anio = self.anio_var.get()
        if not anio:
            return
        
        from models.materias import get_materias_por_anio
        materias = get_materias_por_anio(int(anio))
        self.materia_combo['values'] = materias
        self.materia_var.set("")
        self.profesor_var.set("")
        self.comision_var.set("")
        self.horario_var.set("")

    def _on_materia_change(self, event=None):
        """Cargar profesores según materia."""
        materia = self.materia_var.get()
        if not materia:
            return
        
        from models.materias import get_profesores_materia
        profesores = get_profesores_materia(materia)
        self.profesor_combo['values'] = profesores
        self.profesor_var.set("")
        self.comision_var.set("")
        self.horario_var.set("")

    def _on_profesor_change(self, event=None):
        """Cargar comisiones según profesor."""
        materia = self.materia_var.get()
        profesor = self.profesor_var.get()
        if not materia or not profesor:
            return
        
        from models.materias import get_comisiones_profesor
        comisiones = get_comisiones_profesor(materia, profesor)
        self.comision_combo['values'] = comisiones
        self.comision_var.set("")
        self.horario_var.set("")

    def _on_comision_change(self, event=None):
        """Cargar horario automáticamente."""
        materia = self.materia_var.get()
        profesor = self.profesor_var.get()
        comision = self.comision_var.get()
        if not all([materia, profesor, comision]):
            return
        
        from models.materias import get_horario
        horario = get_horario(materia, profesor, comision)
        self.horario_var.set(horario if horario else "Sin horario definido")

    def _guardar(self):
        """Guarda la inscripción."""
        # Validar campos obligatorios
        if not self.nombre_var.get().strip():
            self.show_warning("Validación", "El nombre es obligatorio")
            return
        
        if not self.apellido_var.get().strip():
            self.show_warning("Validación", "El apellido es obligatorio")
            return
        
        if not self.dni_var.get().strip():
            self.show_warning("Validación", "El DNI es obligatorio")
            return
        
        if not self.anio_var.get():
            self.show_warning("Validación", "El año es obligatorio")
            return
        
        if not self.turno_var.get():
            self.show_warning("Validación", "El turno es obligatorio")
            return
        
        if not self.materia_var.get():
            self.show_warning("Validación", "La materia es obligatoria")
            return
        
        if not self.profesor_var.get():
            self.show_warning("Validación", "El profesor es obligatorio")
            return
        
        if not self.comision_var.get():
            self.show_warning("Validación", "La comisión es obligatoria")
            return
        
        # Construir registro
        from datetime import datetime
        import uuid
        
        registro = {
            "id": str(uuid.uuid4()),
            "fecha_inscripcion": datetime.now().isoformat(),
            "nombre": self.nombre_var.get().strip(),
            "apellido": self.apellido_var.get().strip(),
            "dni": self.dni_var.get().strip(),
            "fecha_nacimiento": self.fecha_nac_var.get().strip(),
            "edad": self.edad_var.get().strip(),
            "direccion": self.direccion_var.get().strip(),
            "telefono": self.telefono_var.get().strip(),
            "email": self.email_var.get().strip(),
            "nombre_padre": self.nombre_padre_var.get().strip(),
            "nombre_madre": self.nombre_madre_var.get().strip(),
            "telefono_emergencia": self.telefono_emergencia_var.get().strip(),
            "obra_social": self.obra_social_var.get().strip(),
            "seguro_escolar": self.seguro_escolar_var.get(),
            "turno": self.turno_var.get(),
            "anio": self.anio_var.get(),
            "materia": self.materia_var.get(),
            "profesor": self.profesor_var.get(),
            "comision": self.comision_var.get(),
            "horario": self.horario_var.get().strip(),
            "observaciones": self.observaciones_text.get("1.0", tk.END).strip()
        }
            
        # Guardar en CSV
        from database.csv_handler import guardar_registro
        
        ok, msg = guardar_registro(registro)
        
        if ok:
            self.show_info("Éxito", f"Inscripción guardada correctamente\nID: {registro['id'][:8]}")
            self._limpiar()
            self.refresh()  # ← IMPORTANTE: Actualizar tabla
            self.app.refresh_all()  # ← Actualizar otras pestañas
        else:
            self.show_error("Error", msg)

    def _limpiar(self):
        """Limpia todos los campos del formulario."""
        # Datos personales
        self.nombre_var.set("")
        self.apellido_var.set("")
        self.dni_var.set("")
        self.fecha_nac_var.set("")
        self.edad_var.set("")
        
        # Contacto
        self.direccion_var.set("")
        self.telefono_var.set("")
        self.email_var.set("")
        
        # Responsables
        self.nombre_padre_var.set("")
        self.nombre_madre_var.set("")
        self.telefono_emergencia_var.set("")
        
        # Otros datos
        self.saeta_var.set("No")
        self.obra_social_var.set("")
        self.seguro_escolar_var.set("No")
        self.pago_voluntario_var.set("No")
        self.monto_var.set("")
        self.permiso_var.set("No")
        self.observaciones_text.delete("1.0", tk.END)
        
        # Inscripción
        self.anio_var.set("")
        self.turno_var.set("")
        self.materia_var.set("")
        self.profesor_var.set("")
        self.comision_var.set("")
        self.horario_var.set("")
        
        # Limpiar comboboxes
        self.materia_combo['values'] = []
        self.profesor_combo['values'] = []
        self.comision_combo['values'] = []

    def _generar_certificado(self):
        """Genera certificado PDF de la inscripción actual."""
        # Validar que haya datos mínimos
        if not self.nombre_var.get() or not self.apellido_var.get():
            self.show_warning("Certificado", "Completá al menos nombre y apellido")
            return
        
        # Construir registro temporal
        registro = {
            "nombre": self.nombre_var.get().strip(),
            "apellido": self.apellido_var.get().strip(),
            "dni": self.dni_var.get().strip(),
            "materia": self.materia_var.get(),
            "profesor": self.profesor_var.get(),
            "comision": self.comision_var.get(),
            "turno": self.turno_var.get(),
            "anio": self.anio_var.get(),
            "horario": self.horario_var.get().strip(),
            "seguro_escolar": self.seguro_escolar_var.get(),
            "obra_social": self.obra_social_var.get().strip()
        }
        
        from services.pdf_generator import generar_certificado_pdf
        
        ok, msg = generar_certificado_pdf(registro)
        
        if ok:
            self.show_info("Certificado", msg)
        else:
            self.show_error("Error", msg)