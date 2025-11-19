"""Pestaña de Formulario de Inscripción."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sys
import os
import threading
from ui.base_tab import BaseTab
from database.csv_handler import (
    cargar_registros, guardar_registro, 
    actualizar_registro, eliminar_registro,
    generar_id, contar_inscripciones_materia
)
from models.materias import (
    get_todas_materias,
    get_materias_por_anio,
    get_profesores_materia,
    get_comisiones_profesor,
    get_horario,
    get_turnos_disponibles,
    get_info_completa
)
from services.validators import (
    validar_dni, validar_email, validar_telefono,
    validar_edad_minima, validar_datos_inscripcion
)
from services.pdf_generator import generar_certificado_pdf
from services.email_service import send_certificado_via_email, get_smtp_config
from config.settings import settings, CERTIFICATES_DIR

# Detectar pandas
try:
    import pandas as pd
    _HAS_PANDAS = True
except ImportError:
    _HAS_PANDAS = False


class FormTab(BaseTab):
    """Pestaña de formulario de inscripción."""
                
    def _build_ui(self):
        """Construye la interfaz del formulario SIN scroll."""
        # Contenedor principal
        main_container = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # === PANEL IZQUIERDO: FORMULARIO (SIN CANVAS NI SCROLLBAR) ===
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)
        
        # Contenedor del formulario principal
        form_main = ttk.Frame(left_panel)
        form_main.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Construir secciones en flujo vertical
        self._build_datos_estudiante_compact(form_main)
        self._build_datos_responsable_compact(form_main)
        self._build_datos_inscripcion_compact(form_main)
        
        # Materia section full-width below
        self._build_datos_materia_full_width(form_main)
        
        # Botones abajo
        self._build_buttons(left_panel)
        
        # === PANEL DERECHO: TABLA ===
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)
        self._build_table(right_panel)
        
        # Cargar turnos dinámicamente
        self._cargar_turnos_disponibles()

    def _build_datos_estudiante_compact(self, parent):
        """Construye sección compacta de datos del estudiante."""
        frame = ttk.LabelFrame(parent, text="Datos del Estudiante", padding=5)
        frame.pack(fill=tk.X, pady=(0, 5))
        
        self.entries = {}
        
        # Nombre
        ttk.Label(frame, text="Nombre:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self.entries["nombre"] = ttk.Entry(frame, width=25)
        self.entries["nombre"].grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        
        # Apellido
        ttk.Label(frame, text="Apellido:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self.entries["apellido"] = ttk.Entry(frame, width=25)
        self.entries["apellido"].grid(row=1, column=1, sticky="ew", padx=2, pady=2)
        
        # DNI
        ttk.Label(frame, text="DNI:").grid(row=2, column=0, sticky="e", padx=2, pady=2)
        self.entries["dni"] = ttk.Entry(frame, width=25)
        self.entries["dni"].grid(row=2, column=1, sticky="ew", padx=2, pady=2)
        
        # Legajo
        ttk.Label(frame, text="Legajo:").grid(row=3, column=0, sticky="e", padx=2, pady=2)
        self.entries["legajo"] = ttk.Entry(frame, width=25)
        self.entries["legajo"].grid(row=3, column=1, sticky="ew", padx=2, pady=2)
        
        # Teléfono
        ttk.Label(frame, text="Teléfono:").grid(row=4, column=0, sticky="e", padx=2, pady=2)
        self.entries["telefono"] = ttk.Entry(frame, width=25)
        self.entries["telefono"].grid(row=4, column=1, sticky="ew", padx=2, pady=2)
        
        # Edad
        ttk.Label(frame, text="Edad:").grid(row=5, column=0, sticky="e", padx=2, pady=2)
        self.entries["edad"] = ttk.Entry(frame, width=10)
        self.entries["edad"].grid(row=5, column=1, sticky="w", padx=2, pady=2)
        
        # Domicilio
        ttk.Label(frame, text="Domicilio:").grid(row=6, column=0, sticky="e", padx=2, pady=2)
        self.entries["direccion"] = ttk.Entry(frame, width=25)
        self.entries["direccion"].grid(row=6, column=1, sticky="ew", padx=2, pady=2)
        
        # Mail
        ttk.Label(frame, text="Mail:").grid(row=7, column=0, sticky="e", padx=2, pady=2)
        self.entries["email"] = ttk.Entry(frame, width=25)
        self.entries["email"].grid(row=7, column=1, sticky="ew", padx=2, pady=2)
        
        # Fecha de Nacimiento
        ttk.Label(frame, text="F. Nacimiento:").grid(row=8, column=0, sticky="e", padx=2, pady=2)
        self.entries["fecha_nacimiento"] = ttk.Entry(frame, width=25)
        self.entries["fecha_nacimiento"].grid(row=8, column=1, sticky="ew", padx=2, pady=2)
        
        frame.columnconfigure(1, weight=1)

    def _build_datos_responsable_compact(self, parent):
        """Construye sección compacta de responsables/tutores."""
        frame = ttk.LabelFrame(parent, text="Datos Responsable o Tutor/a", padding=5)
        frame.pack(fill=tk.X, pady=(0, 5))
        
        # Nombre Padre
        ttk.Label(frame, text="Nombre-Padre:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self.entries["nombre_padre"] = ttk.Entry(frame, width=25)
        self.entries["nombre_padre"].grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        
        # Nombre Madre
        ttk.Label(frame, text="Nombre-Madre:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self.entries["nombre_madre"] = ttk.Entry(frame, width=25)
        self.entries["nombre_madre"].grid(row=1, column=1, sticky="ew", padx=2, pady=2)
        
        # Contacto Tutor
        ttk.Label(frame, text="Contacto Tutor:").grid(row=2, column=0, sticky="e", padx=2, pady=2)
        self.entries["telefono_emergencia"] = ttk.Entry(frame, width=25)
        self.entries["telefono_emergencia"].grid(row=2, column=1, sticky="ew", padx=2, pady=2)
        
        frame.columnconfigure(1, weight=1)

    def _build_datos_inscripcion_compact(self, parent):
        """Construye sección compacta de datos de inscripción."""
        frame = ttk.LabelFrame(parent, text="Datos de Inscripción", padding=5)
        frame.pack(fill=tk.X, pady=(0, 5))
        
        # Fila 1: SAETA y Obra Social
        ttk.Label(frame, text="SAETA:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self.saeta_var = tk.StringVar(value="No")
        ttk.Combobox(frame, textvariable=self.saeta_var, values=["No", "Sí"], 
                     state="readonly", width=10).grid(row=0, column=1, sticky="w", padx=2, pady=2)
        
        ttk.Label(frame, text="Obra Social:").grid(row=0, column=2, sticky="e", padx=2, pady=2)
        self.entries["obra_social"] = ttk.Entry(frame, width=12)
        self.entries["obra_social"].grid(row=0, column=3, sticky="ew", padx=2, pady=2)
        
        # Fila 2: Seguro Escolar y Pago Voluntario
        ttk.Label(frame, text="Seguro Escolar:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self.seguro_escolar_var = tk.StringVar(value="No")
        ttk.Combobox(frame, textvariable=self.seguro_escolar_var, values=["No", "Sí"], 
                     state="readonly", width=10).grid(row=1, column=1, sticky="w", padx=2, pady=2)
        
        ttk.Label(frame, text="Pago Voluntario:").grid(row=1, column=2, sticky="e", padx=2, pady=2)
        self.pago_voluntario_var = tk.StringVar(value="No")
        ttk.Combobox(frame, textvariable=self.pago_voluntario_var, values=["No", "Sí"], 
                     state="readonly", width=10).grid(row=1, column=3, sticky="w", padx=2, pady=2)
        
        # Fila 3: Monto y Permiso
        ttk.Label(frame, text="Monto:").grid(row=2, column=0, sticky="e", padx=2, pady=2)
        self.entries["monto"] = ttk.Entry(frame, width=10)
        self.entries["monto"].grid(row=2, column=1, sticky="w", padx=2, pady=2)
        
        ttk.Label(frame, text="Permiso:").grid(row=2, column=2, sticky="e", padx=2, pady=2)
        self.permiso_var = tk.StringVar(value="No")
        ttk.Combobox(frame, textvariable=self.permiso_var, values=["No", "Sí"], 
                     state="readonly", width=10).grid(row=2, column=3, sticky="w", padx=2, pady=2)
        
        frame.columnconfigure(3, weight=1)

    def _build_datos_materia_full_width(self, parent):
        """Construye sección de materia en ancho completo."""
        frame = ttk.LabelFrame(parent, text="Datos Materia", padding=5)
        frame.pack(fill=tk.X, pady=(5, 0))
        
        # Fila 1: Año y Turno
        ttk.Label(frame, text="Año:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self.anio_var = tk.StringVar()
        self.anio_combo = ttk.Combobox(frame, textvariable=self.anio_var, values=["1","2","3","4"], 
                                        state="readonly", width=8)
        self.anio_combo.grid(row=0, column=1, sticky="w", padx=2, pady=2)
        self.anio_combo.bind("<<ComboboxSelected>>", self._on_anio_change)
        
        ttk.Label(frame, text="Turno:").grid(row=0, column=2, sticky="e", padx=2, pady=2)
        self.turno_var = tk.StringVar()
        self.turno_combo = ttk.Combobox(frame, textvariable=self.turno_var, values=[], 
                     state="readonly", width=12)
        self.turno_combo.grid(row=0, column=3, sticky="w", padx=2, pady=2)
        
        # Fila 2: Materia
        ttk.Label(frame, text="Materia:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self.materia_var = tk.StringVar()
        self.materia_combo = ttk.Combobox(frame, textvariable=self.materia_var, values=[], 
                                           state="readonly", width=50)
        self.materia_combo.grid(row=1, column=1, columnspan=5, sticky="ew", padx=2, pady=2)
        self.materia_combo.bind("<<ComboboxSelected>>", self._on_materia_change)
        
        # Fila 3: Profesor y Comisión (Comisión después de Profesor)
        ttk.Label(frame, text="Profesor/a:").grid(row=2, column=0, sticky="e", padx=2, pady=2)
        self.profesor_var = tk.StringVar()
        self.profesor_combo = ttk.Combobox(frame, textvariable=self.profesor_var, values=[], 
                                            state="readonly", width=25)
        self.profesor_combo.grid(row=2, column=1, columnspan=2, sticky="ew", padx=2, pady=2)
        self.profesor_combo.bind("<<ComboboxSelected>>", self._on_profesor_change)
        
        ttk.Label(frame, text="Comisión:").grid(row=2, column=3, sticky="e", padx=2, pady=2)
        self.comision_var = tk.StringVar()
        self.comision_combo = ttk.Combobox(frame, textvariable=self.comision_var, values=[], 
                                            state="readonly", width=12)
        self.comision_combo.grid(row=2, column=4, sticky="w", padx=2, pady=2)
        self.comision_combo.bind("<<ComboboxSelected>>", self._on_comision_change)
        
        # Fila 4: Horario y Cupo
        ttk.Label(frame, text="Horario:").grid(row=3, column=0, sticky="e", padx=2, pady=2)
        self.horario_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.horario_var, width=30, state="readonly").grid(row=3, column=1, columnspan=2, sticky="ew", padx=2, pady=2)
        
        # Label para mostrar cupo disponible
        ttk.Label(frame, text="Cupo:").grid(row=3, column=3, sticky="e", padx=2, pady=2)
        self.cupo_label = ttk.Label(frame, text="Sin cupo definido", foreground="green")
        self.cupo_label.grid(row=3, column=4, sticky="w", padx=2, pady=2)
        
        # Fila 5: Observaciones (compacto)
        ttk.Label(frame, text="Observaciones:").grid(row=4, column=0, sticky="ne", padx=2, pady=2)
        self.observaciones_text = tk.Text(
            frame, 
            width=50, 
            height=2,
            bg="#3C3C3C",           # Fondo gris oscuro
            fg="#FFFFFF",           # Texto blanco
            insertbackground="#FFFFFF",  # Cursor blanco
            selectbackground="#505050",  # Selección gris
            selectforeground="#FFFFFF",  # Texto seleccionado blanco
            borderwidth=1,
            relief="solid",
            highlightthickness=1,
            highlightcolor="#4A4A4A",
            highlightbackground="#4A4A4A"
        )
        self.observaciones_text.grid(row=4, column=1, columnspan=5, sticky="ew", padx=2, pady=2)
        
        frame.columnconfigure(5, weight=1)

    def _build_buttons(self, parent):
        """Construye sección de botones."""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Botones principales
        ttk.Button(
            buttons_frame,
            text="💾 Guardar Inscripción",
            command=self._guardar
        ).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(
            buttons_frame,
            text="🗑️ Limpiar Formulario",
            command=self._limpiar
        ).grid(row=0, column=1, padx=5, pady=5)
        
        # === NUEVOS BOTONES ===
        ttk.Button(
            buttons_frame,
            text="📧 Generar y Enviar",
            command=self._generar_y_enviar
        ).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(
            buttons_frame,
            text="📄 Generar Certificado",
            command=self._generar_certificado
        ).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(
            buttons_frame,
            text="📊 Exportar Excel",
            command=self._exportar_excel
        ).grid(row=0, column=4, padx=5, pady=5)

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
        
        # Treeview (sin ID visible, con selección múltiple)
        columns = ("Nombre", "Apellido", "DNI", "Materia", "Profesor", "Turno", "Año")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="extended",  # Permite selección múltiple
            height=15
        )
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Diccionario para mapear items del tree a IDs reales
        self.id_map = {}
        
        # Configurar columnas (sin ID)
        column_widths = {
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
        
        # Configurar tags para filas alternas
        self.tree.tag_configure("oddrow", background="#1E1E1E", foreground="#FFFFFF")
        self.tree.tag_configure("evenrow", background="#252525", foreground="#FFFFFF")
        
        # Bind para doble click (cargar estudiante para reinscripción)
        self.tree.bind("<Double-Button-1>", self._cargar_estudiante_dobleclick)
        
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
            command=self._eliminar_seleccionados
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            buttons_frame,
            text="📄 Certificados",
            command=self._generar_certificados_seleccionados
        ).pack(side=tk.LEFT, padx=2)
        
        # === NUEVOS BOTONES ===
        ttk.Button(
            buttons_frame,
            text="📂 Abrir carpeta certificados",
            command=self._abrir_carpeta_certificados
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            buttons_frame,
            text="📧 Enviar certificados",
            command=self._enviar_certificados_seleccionados
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            buttons_frame,
            text="🔄 Refrescar",
            command=self.refresh
        ).pack(side=tk.RIGHT, padx=2)
        
        # Cargar datos iniciales
        self.refresh()

    def _on_anio_change(self, event=None):
        """Al cambiar año, filtrar materias."""
        anio = self.anio_var.get()
        if not anio:
            return
        
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
        
        comisiones = get_comisiones_profesor(materia, profesor)
        self.comision_combo['values'] = comisiones
        self.comision_var.set("")
        self.horario_var.set("")

    def _on_comision_change(self, event=None):
        """Al cambiar comisión, cargar horario y actualizar cupo."""
        materia = self.materia_var.get()
        profesor = self.profesor_var.get()
        comision = self.comision_var.get()
        if not all([materia, profesor, comision]):
            return
        
        horario = get_horario(materia, profesor, comision)
        self.horario_var.set(horario if horario else "Sin horario")
        
        # Actualizar cupo disponible
        self._actualizar_cupo_disponible()
    
    def _cargar_turnos_disponibles(self):
        """Carga los turnos disponibles dinámicamente desde el CSV."""
        try:
            turnos = get_turnos_disponibles()
            if turnos and hasattr(self, 'turno_combo'):
                self.turno_combo['values'] = turnos
        except Exception as e:
            print(f"[WARN] No se pudieron cargar turnos: {e}")
    
    def _actualizar_cupo_disponible(self):
        """Actualiza el label de cupo disponible."""
        materia = self.materia_var.get()
        profesor = self.profesor_var.get()
        comision = self.comision_var.get()
        
        if not all([materia, profesor, comision]):
            self.cupo_label.config(text="Sin cupo definido", foreground="lightgreen")
            return
        
        # Obtener info completa para saber el cupo máximo
        info = get_info_completa(materia, profesor, comision)
        if not info or not info.get("cupo"):
            self.cupo_label.config(text="Sin cupo definido", foreground="lightgreen")
            return
        
        cupo_maximo = info.get("cupo", 0)
        
        # Contar inscripciones actuales (sin lista de espera)
        inscripciones_actuales = contar_inscripciones_materia(materia, profesor, comision)
        
        # Calcular disponibles
        cupo_disponible = cupo_maximo - inscripciones_actuales
        
        if cupo_disponible > 0:
            # Hay cupo disponible
            self.cupo_label.config(
                text=f"Cupo: {cupo_disponible}/{cupo_maximo}",
                foreground="green"
            )
        elif cupo_disponible == 0:
            # Cupo completo
            self.cupo_label.config(
                text=f"Cupo completo ({cupo_maximo}/{cupo_maximo})",
                foreground="orange"
            )
        else:
            # Lista de espera
            en_espera = abs(cupo_disponible)
            self.cupo_label.config(
                text=f"Lista de espera: {en_espera}",
                foreground="red"
            )

    def _guardar(self):
        """Guarda la inscripción."""
        # Validar campos obligatorios
        if not self.entries["nombre"].get().strip():
            self.show_warning("Validación", "El nombre es obligatorio")
            return
        
        if not self.entries["apellido"].get().strip():
            self.show_warning("Validación", "El apellido es obligatorio")
            return
        
        if not self.entries["dni"].get().strip():
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
        
        # Verificar cupo antes de guardar
        materia = self.materia_var.get()
        profesor = self.profesor_var.get()
        comision = self.comision_var.get()
        
        info = get_info_completa(materia, profesor, comision)
        en_lista_espera = "No"
        
        if info and info.get("cupo"):
            cupo_maximo = info.get("cupo", 0)
            inscripciones_actuales = contar_inscripciones_materia(materia, profesor, comision)
            
            if inscripciones_actuales >= cupo_maximo:
                # Cupo completo, preguntar si desea inscribir en lista de espera
                mensaje = f"El cupo está completo ({cupo_maximo}/{cupo_maximo}).\n"
                mensaje += "El estudiante será inscripto en LISTA DE ESPERA.\n¿Desea continuar?"
                
                if not self.ask_yes_no("Cupo completo", mensaje):
                    return
                
                en_lista_espera = "Sí"
        
        # Construir registro básico para generar ID
        registro_temp = {
            "legajo": self.entries["legajo"].get().strip(),
            "dni": self.entries["dni"].get().strip()
        }
        
        # Generar ID con nuevo formato
        nuevo_id = generar_id(registro_temp)
        
        registro = {
            "id": nuevo_id,
            "fecha_inscripcion": datetime.now().isoformat(),
            "nombre": self.entries["nombre"].get().strip(),
            "apellido": self.entries["apellido"].get().strip(),
            "dni": self.entries["dni"].get().strip(),
            "fecha_nacimiento": self.entries["fecha_nacimiento"].get().strip(),
            "edad": self.entries["edad"].get().strip(),
            "legajo": self.entries["legajo"].get().strip(),
            "direccion": self.entries["direccion"].get().strip(),
            "telefono": self.entries["telefono"].get().strip(),
            "email": self.entries["email"].get().strip(),
            "nombre_padre": self.entries["nombre_padre"].get().strip(),
            "nombre_madre": self.entries["nombre_madre"].get().strip(),
            "telefono_emergencia": self.entries["telefono_emergencia"].get().strip(),
            "saeta": self.saeta_var.get(),
            "obra_social": self.entries["obra_social"].get().strip(),
            "seguro_escolar": self.seguro_escolar_var.get(),
            "pago_voluntario": self.pago_voluntario_var.get(),
            "monto": self.entries["monto"].get().strip(),
            "permiso": self.permiso_var.get(),
            "anio": self.anio_var.get(),
            "turno": self.turno_var.get(),
            "materia": self.materia_var.get(),
            "profesor": self.profesor_var.get(),
            "comision": self.comision_var.get(),
            "horario": self.horario_var.get().strip(),
            "observaciones": self.observaciones_text.get("1.0", tk.END).strip(),
            "en_lista_espera": en_lista_espera
        }
        
        # Guardar
        try:
            guardar_registro(registro)
            mensaje_exito = f"Inscripción guardada correctamente\nID: {nuevo_id}"
            if en_lista_espera == "Sí":
                mensaje_exito += "\n⚠️ INSCRIPTO EN LISTA DE ESPERA"
            self.show_info("Éxito", mensaje_exito)
            self._limpiar()
            self.refresh()
            self.app.refresh_all()
        except Exception as e:
            self.show_error("Error", f"No se pudo guardar: {e}")

    def _limpiar(self):
        """Limpia todos los campos del formulario."""
        # Limpiar entries
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        # Limpiar comboboxes
        self.saeta_var.set("No")
        self.seguro_escolar_var.set("No")
        self.pago_voluntario_var.set("No")
        self.permiso_var.set("No")
        self.anio_var.set("")
        self.turno_var.set("")
        self.materia_var.set("")
        self.profesor_var.set("")
        self.comision_var.set("")
        self.horario_var.set("")
        
        # Limpiar observaciones
        self.observaciones_text.delete("1.0", tk.END)

    def _filtrar_tabla(self):
        """Filtra la tabla según el texto de búsqueda."""
        search_text = self.search_var.get().lower()
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Recargar registros filtrados
        registros = cargar_registros()
        
        idx = 0
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
                
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                # Insertar sin ID, pero guardar ID completo en el item
                item_id = self.tree.insert("", tk.END, values=(
                    reg.get("nombre", ""),
                    reg.get("apellido", ""),
                    reg.get("dni", ""),
                    reg.get("materia", ""),
                    reg.get("profesor", ""),
                    reg.get("turno", ""),
                    reg.get("anio", "")
                ), tags=(tag,))
                # Guardar ID en diccionario interno
                self.id_map[item_id] = reg.get("id", "")
                idx += 1

    def _editar_seleccionado(self):
        """Carga el registro seleccionado en el formulario para editar."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Editar", "Selecciona un registro de la tabla")
            return
        
        # Advertencia si hay múltiples seleccionados
        if len(selection) > 1:
            self.show_warning("Editar", "Edición solo funciona con UN registro.\nSelecciona solo uno.")
            return
        
        item_id = selection[0]
        reg_id = self._get_id_from_item(item_id)
        
        # Buscar registro completo por ID
        registros = cargar_registros()
        
        registro = None
        for reg in registros:
            if reg.get("id") == reg_id:
                registro = reg
                break
        
        if not registro:
            self.show_error("Error", "No se encontró el registro completo")
            return
        
        # Cargar datos en el formulario (todos los campos)
        self.entries["nombre"].delete(0, tk.END)
        self.entries["nombre"].insert(0, registro.get("nombre", ""))
        
        self.entries["apellido"].delete(0, tk.END)
        self.entries["apellido"].insert(0, registro.get("apellido", ""))
        
        self.entries["dni"].delete(0, tk.END)
        self.entries["dni"].insert(0, registro.get("dni", ""))
        
        self.entries["fecha_nacimiento"].delete(0, tk.END)
        self.entries["fecha_nacimiento"].insert(0, registro.get("fecha_nacimiento", ""))
        
        self.entries["edad"].delete(0, tk.END)
        self.entries["edad"].insert(0, registro.get("edad", ""))
        
        self.entries["legajo"].delete(0, tk.END)
        self.entries["legajo"].insert(0, registro.get("legajo", ""))
        
        self.entries["telefono"].delete(0, tk.END)
        self.entries["telefono"].insert(0, registro.get("telefono", ""))
        
        self.entries["direccion"].delete(0, tk.END)
        self.entries["direccion"].insert(0, registro.get("direccion", ""))
        
        self.entries["email"].delete(0, tk.END)
        self.entries["email"].insert(0, registro.get("email", ""))
        
        self.entries["nombre_padre"].delete(0, tk.END)
        self.entries["nombre_padre"].insert(0, registro.get("nombre_padre", ""))
        
        self.entries["nombre_madre"].delete(0, tk.END)
        self.entries["nombre_madre"].insert(0, registro.get("nombre_madre", ""))
        
        self.entries["telefono_emergencia"].delete(0, tk.END)
        self.entries["telefono_emergencia"].insert(0, registro.get("telefono_emergencia", ""))
        
        self.entries["obra_social"].delete(0, tk.END)
        self.entries["obra_social"].insert(0, registro.get("obra_social", ""))
        
        self.entries["monto"].delete(0, tk.END)
        self.entries["monto"].insert(0, registro.get("monto", ""))
        
        self.saeta_var.set(registro.get("saeta", "No"))
        self.seguro_escolar_var.set(registro.get("seguro_escolar", "No"))
        self.pago_voluntario_var.set(registro.get("pago_voluntario", "No"))
        self.permiso_var.set(registro.get("permiso", "No"))
        
        # Cargar datos de materia
        self.anio_var.set(registro.get("anio", ""))
        self.turno_var.set(registro.get("turno", ""))
        self.materia_var.set(registro.get("materia", ""))
        self.profesor_var.set(registro.get("profesor", ""))
        self.comision_var.set(registro.get("comision", ""))
        self.horario_var.set(registro.get("horario", ""))
        
        # Cargar observaciones
        self.observaciones_text.delete("1.0", tk.END)
        self.observaciones_text.insert("1.0", registro.get("observaciones", ""))
        
        self.show_info("Editar", "Registro cargado. Modifica los campos y guarda.")



    def refresh(self):
        """Refresca la tabla con los registros guardados."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar registros desde CSV
        registros = cargar_registros()
        
        # Limpiar mapa antes de recargar
        self.id_map = {}
        
        # Poblar tabla con filas alternas (sin ID visible)
        for idx, reg in enumerate(registros):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            item_id = self.tree.insert("", tk.END, values=(
                reg.get("nombre", ""),
                reg.get("apellido", ""),
                reg.get("dni", ""),
                reg.get("materia", ""),
                reg.get("profesor", ""),
                reg.get("turno", ""),
                reg.get("anio", "")
            ), tags=(tag,))
            # Guardar ID en diccionario interno
            self.id_map[item_id] = reg.get("id", "")
    
    def _get_id_from_item(self, item_id):
        """Obtiene el ID completo de un item del tree."""
        return self.id_map.get(item_id, "")
    
    def _cargar_estudiante_dobleclick(self, event):
        """Carga datos del estudiante (sin materia) al hacer doble click."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        reg_id = self._get_id_from_item(item_id)
        
        # Buscar registro completo
        registros = cargar_registros()
        registro = None
        for reg in registros:
            if reg.get("id") == reg_id:
                registro = reg
                break
        
        if not registro:
            return
        
        # Cargar solo datos personales (no materia)
        self.entries["nombre"].delete(0, tk.END)
        self.entries["nombre"].insert(0, registro.get("nombre", ""))
        
        self.entries["apellido"].delete(0, tk.END)
        self.entries["apellido"].insert(0, registro.get("apellido", ""))
        
        self.entries["dni"].delete(0, tk.END)
        self.entries["dni"].insert(0, registro.get("dni", ""))
        
        self.entries["legajo"].delete(0, tk.END)
        self.entries["legajo"].insert(0, registro.get("legajo", ""))
        
        self.entries["telefono"].delete(0, tk.END)
        self.entries["telefono"].insert(0, registro.get("telefono", ""))
        
        self.entries["edad"].delete(0, tk.END)
        self.entries["edad"].insert(0, registro.get("edad", ""))
        
        self.entries["direccion"].delete(0, tk.END)
        self.entries["direccion"].insert(0, registro.get("direccion", ""))
        
        self.entries["email"].delete(0, tk.END)
        self.entries["email"].insert(0, registro.get("email", ""))
        
        self.entries["fecha_nacimiento"].delete(0, tk.END)
        self.entries["fecha_nacimiento"].insert(0, registro.get("fecha_nacimiento", ""))
        
        self.entries["nombre_padre"].delete(0, tk.END)
        self.entries["nombre_padre"].insert(0, registro.get("nombre_padre", ""))
        
        self.entries["nombre_madre"].delete(0, tk.END)
        self.entries["nombre_madre"].insert(0, registro.get("nombre_madre", ""))
        
        self.entries["telefono_emergencia"].delete(0, tk.END)
        self.entries["telefono_emergencia"].insert(0, registro.get("telefono_emergencia", ""))
        
        self.entries["obra_social"].delete(0, tk.END)
        self.entries["obra_social"].insert(0, registro.get("obra_social", ""))
        
        self.entries["monto"].delete(0, tk.END)
        self.entries["monto"].insert(0, registro.get("monto", ""))
        
        self.saeta_var.set(registro.get("saeta", "No"))
        self.seguro_escolar_var.set(registro.get("seguro_escolar", "No"))
        self.pago_voluntario_var.set(registro.get("pago_voluntario", "No"))
        self.permiso_var.set(registro.get("permiso", "No"))
        
        # NO cargar datos de materia (para reinscripción)
        self.show_info("Datos cargados", 
                      f"Datos de {registro.get('nombre')} {registro.get('apellido')} cargados.\n"
                      "Selecciona nueva materia para reinscribir.")
    
    def _eliminar_seleccionados(self):
        """Elimina los registros seleccionados (soporte multi-selección)."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Eliminar", "Selecciona al menos un registro")
            return
        
        count = len(selection)
        mensaje = f"¿Estás seguro de eliminar {count} inscripción(es)?"
        
        if not self.ask_yes_no("Confirmar eliminación", mensaje):
            return
        
        # Obtener IDs a eliminar
        ids_to_delete = []
        for item_id in selection:
            reg_id = self._get_id_from_item(item_id)
            ids_to_delete.append(reg_id)
        
        # Cargar registros y filtrar
        registros = cargar_registros()
        registros_filtrados = [
            reg for reg in registros 
            if reg.get("id") not in ids_to_delete
        ]
        
        from database.csv_handler import guardar_todos_registros
        ok, msg = guardar_todos_registros(registros_filtrados)
        
        if ok:
            self.show_info("Eliminado", f"{count} registro(s) eliminado(s) correctamente")
            self.refresh()
            self.app.refresh_all()
        else:
            self.show_error("Error", msg)
    
    def _generar_certificados_seleccionados(self):
        """Genera certificados para todos los registros seleccionados."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Certificados", "Selecciona al menos un registro")
            return
        
        count = len(selection)
        exitosos = 0
        
        registros = cargar_registros()
        
        for item_id in selection:
            reg_id = self._get_id_from_item(item_id)
            
            # Buscar registro completo
            registro = None
            for reg in registros:
                if reg.get("id") == reg_id:
                    registro = reg
                    break
            
            if registro:
                ok, msg = generar_certificado_pdf(registro)
                if ok:
                    exitosos += 1
        
        self.show_info("Certificados", f"{exitosos} de {count} certificado(s) generado(s)")
    
    def _enviar_certificados_seleccionados(self):
        """Envía certificados por email para todos los seleccionados."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Enviar", "Selecciona al menos un registro")
            return
        
        # Verificar SMTP
        smtp_cfg = get_smtp_config()
        if not smtp_cfg.get("username") or not smtp_cfg.get("password"):
            self.show_warning("SMTP no configurado", 
                             "Configurá SMTP en la pestaña Configuración")
            return
        
        count = len(selection)
        registros = cargar_registros()
        
        def worker():
            exitosos = 0
            for item_id in selection:
                reg_id = self._get_id_from_item(item_id)
                
                # Buscar registro completo
                registro = None
                for reg in registros:
                    if reg.get("id") == reg_id:
                        registro = reg
                        break
                
                if registro and registro.get("email"):
                    # Generar PDF
                    ok, result = generar_certificado_pdf(registro)
                    if ok:
                        pdf_path = result
                        # Enviar email
                        ok_email, msg = send_certificado_via_email(registro, pdf_path, smtp_cfg)
                        if ok_email:
                            exitosos += 1
            
            def finish():
                self.show_info("Enviados", f"{exitosos} de {count} certificado(s) enviado(s)")
            
            try:
                self.app.root.after(1, finish)
            except:
                finish()
        
        threading.Thread(target=worker, daemon=True).start()
        self.show_info("Enviando", f"Enviando {count} certificado(s) en segundo plano...")

    # ============= NUEVOS MÉTODOS =============

    def _leer_campos(self):
        """Lee y retorna dict con todos los campos del formulario."""
        campos = {}
        
        # Leer entries (campos de texto)
        for key, entry in self.entries.items():
            try:
                campos[key] = entry.get().strip()
            except:
                campos[key] = ""
        
        # Leer comboboxes y variables
        campos["anio"] = self.anio_var.get() if hasattr(self, "anio_var") else ""
        campos["turno"] = self.turno_var.get() if hasattr(self, "turno_var") else ""
        campos["materia"] = self.materia_var.get() if hasattr(self, "materia_var") else ""
        campos["profesor"] = self.profesor_var.get() if hasattr(self, "profesor_var") else ""
        campos["comision"] = self.comision_var.get() if hasattr(self, "comision_var") else ""
        campos["horario"] = self.horario_var.get() if hasattr(self, "horario_var") else ""
        campos["saeta"] = self.saeta_var.get() if hasattr(self, "saeta_var") else "No"
        campos["seguro_escolar"] = self.seguro_escolar_var.get() if hasattr(self, "seguro_escolar_var") else "No"
        campos["pago_voluntario"] = self.pago_voluntario_var.get() if hasattr(self, "pago_voluntario_var") else "No"
        campos["permiso"] = self.permiso_var.get() if hasattr(self, "permiso_var") else "No"
        
        # Observaciones (Text widget)
        if hasattr(self, "observaciones_text"):
            try:
                campos["observaciones"] = self.observaciones_text.get("1.0", tk.END).strip()
            except:
                campos["observaciones"] = ""
        
        return campos

    def _generar_y_enviar(self):
        """Genera certificado y lo envía por email."""
        try:
            campos = self._leer_campos()
        except Exception as e:
            self.show_error("Error", f"No se pudieron leer los campos: {e}")
            return
        
        # Validar datos mínimos
        if not campos.get("nombre") or not campos.get("apellido"):
            self.show_error("Datos incompletos", "Falta nombre o apellido")
            return
        
        if not campos.get("email"):
            self.show_error("Sin email", "El estudiante no tiene email configurado")
            return
        
        # Construir registro
        registro = {
            "id": campos.get("legajo", ""),
            "fecha_inscripcion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **campos
        }
        
        # Generar PDF
        ok, result = generar_certificado_pdf(registro)
        if not ok:
            self.show_error("Error al generar", result)
            return
        
        pdf_path = result
        
        # Obtener configuración SMTP
        smtp_cfg = get_smtp_config()
        if not smtp_cfg.get("username") or not smtp_cfg.get("password"):
            self.show_warning("SMTP no configurado", 
                             "Configurá SMTP en la pestaña Configuración")
            return
        
        # Enviar en background
        def worker():
            ok_email, msg = send_certificado_via_email(registro, pdf_path, smtp_cfg)
            
            def finish():
                if ok_email:
                    self.show_info("Email enviado", msg)
                else:
                    self.show_error("Error al enviar", msg)
            
            try:
                self.app.root.after(1, finish)
            except:
                finish()
        
        threading.Thread(target=worker, daemon=True).start()
        self.show_info("Envío en background", 
                       "El certificado se está enviando en segundo plano")

    def _generar_certificado(self):
        """Genera certificado sin enviar."""
        try:
            campos = self._leer_campos()
        except Exception as e:
            self.show_error("Error", f"No se pudieron leer los campos: {e}")
            return
        
        if not campos.get("nombre") or not campos.get("apellido"):
            self.show_error("Datos incompletos", "Falta nombre o apellido")
            return
        
        registro = {
            "id": campos.get("legajo", ""),
            "fecha_inscripcion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **campos
        }
        
        ok, result = generar_certificado_pdf(registro)
        if not ok:
            self.show_error("Error", result)
            return
        
        self.show_info("Certificado generado", f"Archivo: {result}")
        
        # Abrir PDF automáticamente
        try:
            path = str(result)
            if sys.platform.startswith("darwin"):
                os.system(f"open '{path}'")
            elif os.name == "nt":
                os.startfile(path)
            else:
                os.system(f"xdg-open '{path}'")
        except Exception as e:
            print(f"[WARN] No se pudo abrir el PDF: {e}")

    def _exportar_excel(self):
        """Exporta todos los registros a Excel."""
        registros = cargar_registros()
        if not registros:
            self.show_info("Sin datos", "No hay registros para exportar")
            return
        
        if _HAS_PANDAS:
            # Exportar a Excel
            out_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx")],
                initialfile=f"inscripciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if not out_path:
                return
            
            try:
                df = pd.DataFrame(registros)
                df.to_excel(out_path, index=False)
                self.show_info("Exportado", f"Exportado a: {out_path}")
            except Exception as e:
                self.show_error("Error", f"No se pudo crear Excel: {e}")
        else:
            # Ofrecer CSV como alternativa
            if self.ask_yes_no("Pandas no instalado", 
                              "pandas no está instalado.\n¿Desea exportar a CSV en su lugar?"):
                out_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV", "*.csv")],
                    initialfile=f"inscripciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                )
                
                if not out_path:
                    return
                
                try:
                    import csv
                    from config.settings import CSV_FIELDS
                    
                    with open(out_path, "w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
                        writer.writeheader()
                        for r in registros:
                            writer.writerow(r)
                    
                    self.show_info("Exportado", f"CSV exportado: {out_path}")
                except Exception as e:
                    self.show_error("Error", f"No se pudo exportar: {e}")
            else:
                self.show_info("Cancelado", "Instalá pandas para exportar a Excel:\npip install pandas openpyxl")

    def _abrir_carpeta_certificados(self):
        """Abre la carpeta de certificados en el explorador."""
        try:
            path = str(CERTIFICATES_DIR.resolve())
            
            # Crear carpeta si no existe
            CERTIFICATES_DIR.mkdir(parents=True, exist_ok=True)
            
            if sys.platform.startswith("darwin"):
                os.system(f"open '{path}'")
            elif os.name == "nt":
                os.startfile(path)
            else:
                os.system(f'xdg-open "{path}"')
        except Exception as e:
            self.show_error("Error", f"No se pudo abrir la carpeta: {e}")

