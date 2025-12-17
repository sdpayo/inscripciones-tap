"""Pestaña de Formulario de Inscripción."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sys
import os
import re
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
    get_info_completa
)
from services.validators import (
    validar_dni, validar_email, validar_telefono,
    validar_edad_minima, validar_datos_inscripcion
)
from services.pdf_generator import generar_certificado_pdf
from services.email_service import send_certificado_via_email, get_smtp_config
# sync helper is optional; call wrapped in try/except when used
from config.settings import settings, CERTIFICATES_DIR

# Detectar pandas
try:
    import pandas as pd
    _HAS_PANDAS = True
except ImportError:
    _HAS_PANDAS = False

# ScrollableFrame
try:
    from ui.scrollable import ScrollableFrame
    _HAS_SCROLLABLE = True
except Exception:
    _HAS_SCROLLABLE = False


class FormTab(BaseTab):
    """Pestaña de formulario de inscripción."""

    def _build_ui(self):
        """Construye la interfaz del formulario."""
        main_container = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left: form (scrollable)
        if _HAS_SCROLLABLE:
            left_panel = ScrollableFrame(main_container, vertical=True)
        else:
            left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)

        # contenido interior del panel (wrapper para paddings y para que las llamadas
        # a .pack() de las secciones sigan funcionando)
        if _HAS_SCROLLABLE:
            form_main_wrapper = ttk.Frame(left_panel.inner)
        else:
            form_main_wrapper = ttk.Frame(left_panel)
        form_main_wrapper.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Build compact vertical sections (estudiante, responsable, inscripción)
        self._build_datos_estudiante_compact(form_main_wrapper)
        self._build_datos_responsable_compact(form_main_wrapper)
        self._build_datos_inscripcion_compact(form_main_wrapper)
        self._build_datos_materia_full_width(form_main_wrapper)

        # Buttons under left panel (usar el wrapper para que estén dentro del scroll)
        self._build_buttons(form_main_wrapper)

        # Right: table
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)
        self._build_table(right_panel)

        import threading as _threading_for_lock
        self._sync_lock = threading.Lock()

    def _build_datos_estudiante_compact(self, parent):
        frame = ttk.LabelFrame(parent, text="Datos del Estudiante", padding=5)
        frame.pack(fill=tk.X, pady=(0, 5))

        self.entries = {}

        ttk.Label(frame, text="Nombre:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self.entries["nombre"] = ttk.Entry(frame, width=25)
        self.entries["nombre"].grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(frame, text="Apellido:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self.entries["apellido"] = ttk.Entry(frame, width=25)
        self.entries["apellido"].grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(frame, text="DNI:").grid(row=2, column=0, sticky="e", padx=2, pady=2)
        self.entries["dni"] = ttk.Entry(frame, width=25)
        self.entries["dni"].grid(row=2, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(frame, text="Legajo:").grid(row=3, column=0, sticky="e", padx=2, pady=2)
        self.entries["legajo"] = ttk.Entry(frame, width=25)
        self.entries["legajo"].grid(row=3, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(frame, text="Teléfono:").grid(row=4, column=0, sticky="e", padx=2, pady=2)
        self.entries["telefono"] = ttk.Entry(frame, width=25)
        self.entries["telefono"].grid(row=4, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(frame, text="Edad:").grid(row=5, column=0, sticky="e", padx=2, pady=2)
        self.entries["edad"] = ttk.Entry(frame, width=10)
        self.entries["edad"].grid(row=5, column=1, sticky="w", padx=2, pady=2)

        ttk.Label(frame, text="Domicilio:").grid(row=6, column=0, sticky="e", padx=2, pady=2)
        self.entries["direccion"] = ttk.Entry(frame, width=25)
        self.entries["direccion"].grid(row=6, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(frame, text="Mail:").grid(row=7, column=0, sticky="e", padx=2, pady=2)
        self.entries["email"] = ttk.Entry(frame, width=25)
        self.entries["email"].grid(row=7, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(frame, text="F. Nacimiento:").grid(row=8, column=0, sticky="e", padx=2, pady=2)
        self.entries["fecha_nacimiento"] = ttk.Entry(frame, width=25)
        self.entries["fecha_nacimiento"].grid(row=8, column=1, sticky="ew", padx=2, pady=2)

        frame.columnconfigure(1, weight=1)

    def _build_datos_responsable_compact(self, parent):
        frame = ttk.LabelFrame(parent, text="Datos Responsable o Tutor/a", padding=5)
        frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(frame, text="Nombre-Padre:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self.entries["nombre_padre"] = ttk.Entry(frame, width=25)
        self.entries["nombre_padre"].grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(frame, text="Nombre-Madre:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self.entries["nombre_madre"] = ttk.Entry(frame, width=25)
        self.entries["nombre_madre"].grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(frame, text="Contacto Tutor:").grid(row=2, column=0, sticky="e", padx=2, pady=2)
        self.entries["telefono_emergencia"] = ttk.Entry(frame, width=25)
        self.entries["telefono_emergencia"].grid(row=2, column=1, sticky="ew", padx=2, pady=2)

        frame.columnconfigure(1, weight=1)

    def _build_datos_inscripcion_compact(self, parent):
        frame = ttk.LabelFrame(parent, text="Datos de Inscripción", padding=5)
        frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(frame, text="SAETA:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self.saeta_var = tk.StringVar(value="No")
        ttk.Combobox(frame, textvariable=self.saeta_var, values=["No", "Sí"],
                     state="readonly", width=10).grid(row=0, column=1, sticky="w", padx=2, pady=2)

        ttk.Label(frame, text="Obra Social:").grid(row=0, column=2, sticky="e", padx=2, pady=2)
        self.entries["obra_social"] = ttk.Entry(frame, width=12)
        self.entries["obra_social"].grid(row=0, column=3, sticky="ew", padx=2, pady=2)

        ttk.Label(frame, text="Seguro Escolar:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self.seguro_escolar_var = tk.StringVar(value="No")
        ttk.Combobox(frame, textvariable=self.seguro_escolar_var, values=["No", "Sí"],
                     state="readonly", width=10).grid(row=1, column=1, sticky="w", padx=2, pady=2)

        ttk.Label(frame, text="Pago Voluntario:").grid(row=1, column=2, sticky="e", padx=2, pady=2)
        self.pago_voluntario_var = tk.StringVar(value="No")
        ttk.Combobox(frame, textvariable=self.pago_voluntario_var, values=["No", "Sí"],
                     state="readonly", width=10).grid(row=1, column=3, sticky="w", padx=2, pady=2)

        ttk.Label(frame, text="Monto:").grid(row=2, column=0, sticky="e", padx=2, pady=2)
        self.entries["monto"] = ttk.Entry(frame, width=10)
        self.entries["monto"].grid(row=2, column=1, sticky="w", padx=2, pady=2)

        ttk.Label(frame, text="Permiso:").grid(row=2, column=2, sticky="e", padx=2, pady=2)
        self.permiso_var = tk.StringVar(value="No")
        ttk.Combobox(frame, textvariable=self.permiso_var, values=["No", "Sí"],
                     state="readonly", width=10).grid(row=2, column=3, sticky="w", padx=2, pady=2)

        frame.columnconfigure(3, weight=1)

    def _build_datos_materia_full_width(self, parent):
        frame = ttk.LabelFrame(parent, text="Datos Materia", padding=5)
        frame.pack(fill=tk.X, pady=(5, 0))

        # Año (turno interno)
        ttk.Label(frame, text="Año:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self.anio_var = tk.StringVar()
        self.anio_combo = ttk.Combobox(frame, textvariable=self.anio_var, values=["1", "2", "3", "4"],
                                       state="readonly", width=8)
        self.anio_combo.grid(row=0, column=1, sticky="w", padx=2, pady=2)
        self.anio_combo.bind("<<ComboboxSelected>>", self._on_anio_change)

        # Turno internal (no visible combobox required)
        if not hasattr(self, "turno_var"):
            self.turno_var = tk.StringVar()

        ttk.Label(frame, text="Materia:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self.materia_var = tk.StringVar()
        self.materia_combo = ttk.Combobox(frame, textvariable=self.materia_var, values=[],
                                          state="readonly", width=50)
        self.materia_combo.grid(row=1, column=1, columnspan=5, sticky="ew", padx=2, pady=2)
        self.materia_combo.bind("<<ComboboxSelected>>", self._on_materia_change)

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

        ttk.Label(frame, text="Horario:").grid(row=3, column=0, sticky="e", padx=2, pady=2)
        self.horario_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.horario_var, width=30, state="readonly").grid(
            row=3, column=1, columnspan=2, sticky="ew", padx=2, pady=2
        )

        ttk.Label(frame, text="Cupo:").grid(row=3, column=3, sticky="e", padx=2, pady=2)
        self.cupo_label = ttk.Label(frame, text="Sin cupo definido", foreground="green")
        self.cupo_label.grid(row=3, column=4, sticky="w", padx=2, pady=2)

        ttk.Label(frame, text="Observaciones:").grid(row=4, column=0, sticky="ne", padx=2, pady=2)
        self.observaciones_text = tk.Text(
            frame, width=50, height=2, bg="#3C3C3C", fg="#FFFFFF",
            insertbackground="#FFFFFF", selectbackground="#505050", selectforeground="#FFFFFF",
            borderwidth=1, relief="solid", highlightthickness=1,
            highlightcolor="#4A4A4A", highlightbackground="#4A4A4A"
        )
        self.observaciones_text.grid(row=4, column=1, columnspan=5, sticky="ew", padx=2, pady=2)
        frame.columnconfigure(5, weight=1)

        # Inicializar cupo al construir la UI
        try:
            self._actualizar_cupo_disponible()
        except Exception:
            pass

    def _build_buttons(self, parent):
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(buttons_frame, text="💾 Guardar", command=self._guardar).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(buttons_frame, text="🗑️ Limpiar", command=self._limpiar).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(buttons_frame, text="📧 Generar y Enviar", command=self._generar_y_enviar).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(buttons_frame, text="📄 Generar Certificado", command=self._generar_certificado).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(buttons_frame, text="📊 Excel", command=self._exportar_excel).grid(row=0, column=4, padx=5, pady=5)

    def _build_table(self, parent):
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(header_frame, text="Inscripciones Registradas", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)

        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT)
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._filtrar_tabla())
        ttk.Entry(search_frame, textvariable=self.search_var, width=25).pack(side=tk.LEFT)

        table_frame = ttk.Frame(container)
        table_frame.pack(fill=tk.BOTH, expand=True)

        tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        tree_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")

        # Columns include visible ID (short) to keep behavior consistent
        columns = ("ID", "Nombre", "Apellido", "DNI", "Materia", "Profesor", "Turno", "Año")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                 yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set, height=15)

        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        column_widths = {"ID": 80, "Nombre": 120, "Apellido": 120, "DNI": 100,
                         "Materia": 200, "Profesor": 150, "Turno": 80, "Año": 50}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col], anchor="w")

        self.tree.tag_configure("oddrow", background="#1E1E1E", foreground="#FFFFFF")
        self.tree.tag_configure("evenrow", background="#252525", foreground="#FFFFFF")

        # Map to store full IDs for each tree item (robust for different layouts)
        self.id_map = {}

        # double-click binds to load student data without materia
        self.tree.bind("<Double-1>", self._cargar_estudiante_dobleclick)

        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.pack(side="bottom", fill="x")

        # Buttons under table
        buttons_frame = ttk.Frame(container)
        buttons_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(buttons_frame, text="✏️ Editar", command=self._editar_seleccionado).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="🗑️ Eliminar", command=self._eliminar_seleccionado).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="📄 Certificado", command=self._generar_certificado_seleccionado).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="📂 Carpeta Certificados", command=self._abrir_carpeta_certificados).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="📧 Enviar certificado", command=self._enviar_certificado_seleccionado).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="🔄 Sincronizar", command=self._sincronizar).pack(side=tk.RIGHT, padx=2)

        # populate
        self.refresh()

    # ---------------- Helpers and actions (robust) ----------------

    def _get_id_from_item(self, item_id):
        """Obtiene el ID completo associado al item (string)."""
        try:
            if hasattr(self, "id_map") and item_id in getattr(self, "id_map"):
                return str(self.id_map.get(item_id, ""))
        except Exception:
            pass
        try:
            vals = self.tree.item(item_id).get("values") or []
        except Exception:
            vals = []
        if not vals:
            return ""
        return str(vals[0])

    def _filtrar_tabla(self):
        """Filtra la tabla según el texto de búsqueda (robusto ante tipos mixtos)."""
        search_text = (self.search_var.get() or "").lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        # reset id_map
        self.id_map = {}

        registros = cargar_registros()
        idx = 0
        for reg in registros:
            nombre = str(reg.get("nombre", "") or "").lower()
            apellido = str(reg.get("apellido", "") or "").lower()
            dni = str(reg.get("dni", "") or "").lower()
            materia = str(reg.get("materia", "") or "").lower()

            if (search_text in nombre or search_text in apellido or search_text in dni or search_text in materia):
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                id_display = str(reg.get("id", ""))[:8]
                item_id = self.tree.insert("", tk.END, values=(
                    id_display,
                    reg.get("nombre", ""),
                    reg.get("apellido", ""),
                    reg.get("dni", ""),
                    reg.get("materia", ""),
                    reg.get("profesor", ""),
                    reg.get("turno", ""),
                    reg.get("anio", "")
                ), tags=(tag,))
                self.id_map[item_id] = str(reg.get("id", ""))
                idx += 1

    def _editar_seleccionado(self):
        """Carga el registro seleccionado en el formulario para editar."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Editar", "Selecciona un registro de la tabla")
            return

        if len(selection) > 1:
            self.show_warning("Editar", "Edición solo funciona con UN registro.\nSelecciona solo uno.")
            return

        item_id = selection[0]
        reg_id = self._get_id_from_item(item_id)
        if not reg_id:
            self.show_error("Error", "No se pudo obtener el ID del item seleccionado")
            return

        registros = cargar_registros()
        registro = None
        for reg in registros:
            if str(reg.get("id", "")) == str(reg_id) or str(reg.get("id", "")).startswith(str(reg_id)):
                registro = reg
                break

        if not registro:
            self.show_error("Error", "No se encontró el registro completo")
            return

        # Load fields (robust: check keys exist)
        try:
            self.entries["nombre"].delete(0, tk.END); self.entries["nombre"].insert(0, registro.get("nombre", ""))
            self.entries["apellido"].delete(0, tk.END); self.entries["apellido"].insert(0, registro.get("apellido", ""))
            self.entries["dni"].delete(0, tk.END); self.entries["dni"].insert(0, registro.get("dni", ""))
            self.entries["fecha_nacimiento"].delete(0, tk.END); self.entries["fecha_nacimiento"].insert(0, registro.get("fecha_nacimiento", ""))
            self.entries["edad"].delete(0, tk.END); self.entries["edad"].insert(0, registro.get("edad", ""))
            self.entries["legajo"].delete(0, tk.END); self.entries["legajo"].insert(0, registro.get("legajo", ""))
            self.entries["telefono"].delete(0, tk.END); self.entries["telefono"].insert(0, registro.get("telefono", ""))
            self.entries["direccion"].delete(0, tk.END); self.entries["direccion"].insert(0, registro.get("direccion", ""))
            self.entries["email"].delete(0, tk.END); self.entries["email"].insert(0, registro.get("email", ""))
        except Exception:
            pass

        try:
            self.entries.get("nombre_padre", ttk.Entry()).delete(0, tk.END)
            self.entries.get("nombre_padre", ttk.Entry()).insert(0, registro.get("nombre_padre", ""))
        except Exception:
            pass

        try:
            self.entries.get("nombre_madre", ttk.Entry()).delete(0, tk.END)
            self.entries.get("nombre_madre", ttk.Entry()).insert(0, registro.get("nombre_madre", ""))
        except Exception:
            pass

        try:
            self.entries.get("telefono_emergencia", ttk.Entry()).delete(0, tk.END)
            self.entries.get("telefono_emergencia", ttk.Entry()).insert(0, registro.get("telefono_emergencia", ""))
        except Exception:
            pass

        try:
            self.entries.get("obra_social", ttk.Entry()).delete(0, tk.END)
            self.entries.get("obra_social", ttk.Entry()).insert(0, registro.get("obra_social", ""))
        except Exception:
            pass

        try:
            self.entries.get("monto", ttk.Entry()).delete(0, tk.END)
            self.entries.get("monto", ttk.Entry()).insert(0, registro.get("monto", ""))
        except Exception:
            pass

        try:
            self.saeta_var.set(registro.get("saeta", "No"))
            self.seguro_escolar_var.set(registro.get("seguro_escolar", "No"))
            self.pago_voluntario_var.set(registro.get("pago_voluntario", "No"))
            self.permiso_var.set(registro.get("permiso", "No"))
        except Exception:
            pass

        # Materia fields (set if present)
        try:
            self.anio_var.set(registro.get("anio", ""))
            if hasattr(self, "turno_var"):
                self.turno_var.set(str(registro.get("turno", "")))
            self.materia_var.set(registro.get("materia", ""))
            self.profesor_var.set(registro.get("profesor", ""))
            self.comision_var.set(registro.get("comision", ""))
            self.horario_var.set(registro.get("horario", ""))
        except Exception:
            pass

        try:
            self.observaciones_text.delete("1.0", tk.END)
            self.observaciones_text.insert("1.0", registro.get("observaciones", ""))
        except Exception:
            pass

        # actualizar cupo después de cargar
        try:
            self._actualizar_cupo_disponible()
        except Exception:
            pass

        self.show_info("Editar", "Registro cargado. Modifica los campos y guarda.")

    def _cargar_estudiante_dobleclick(self, event):
        """Carga datos personales al hacer doble click sin tocar materia."""
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        try:
            self.tree.selection_set(item_id)
        except Exception:
            pass

        reg_id = self._get_id_from_item(item_id)
        if not reg_id:
            return

        registros = cargar_registros()
        registro = None
        for reg in registros:
            if str(reg.get("id", "")) == str(reg_id) or str(reg.get("id", "")).startswith(str(reg_id)):
                registro = reg
                break

        if not registro:
            return

        # Load only personal/responsible fields (no materia)
        try:
            self.entries["nombre"].delete(0, tk.END); self.entries["nombre"].insert(0, registro.get("nombre", ""))
            self.entries["apellido"].delete(0, tk.END); self.entries["apellido"].insert(0, registro.get("apellido", ""))
            self.entries["dni"].delete(0, tk.END); self.entries["dni"].insert(0, registro.get("dni", ""))
            self.entries["legajo"].delete(0, tk.END); self.entries["legajo"].insert(0, registro.get("legajo", ""))
            self.entries["telefono"].delete(0, tk.END); self.entries["telefono"].insert(0, registro.get("telefono", ""))
            self.entries["edad"].delete(0, tk.END); self.entries["edad"].insert(0, registro.get("edad", ""))
            self.entries["direccion"].delete(0, tk.END); self.entries["direccion"].insert(0, registro.get("direccion", ""))
            self.entries["email"].delete(0, tk.END); self.entries["email"].insert(0, registro.get("email", ""))
            self.entries["fecha_nacimiento"].delete(0, tk.END); self.entries["fecha_nacimiento"].insert(0, registro.get("fecha_nacimiento", ""))
            self.entries["nombre_padre"].delete(0, tk.END); self.entries["nombre_padre"].insert(0, registro.get("nombre_padre", ""))
            self.entries["nombre_madre"].delete(0, tk.END); self.entries["nombre_madre"].insert(0, registro.get("nombre_madre", ""))
            self.entries["telefono_emergencia"].delete(0, tk.END); self.entries["telefono_emergencia"].insert(0, registro.get("telefono_emergencia", ""))
            self.entries["obra_social"].delete(0, tk.END); self.entries["obra_social"].insert(0, registro.get("obra_social", ""))
            self.entries["monto"].delete(0, tk.END); self.entries["monto"].insert(0, registro.get("monto", ""))
            self.saeta_var.set(registro.get("saeta", "No")); self.seguro_escolar_var.set(registro.get("seguro_escolar", "No"))
            self.pago_voluntario_var.set(registro.get("pago_voluntario", "No")); self.permiso_var.set(registro.get("permiso", "No"))
        except Exception:
            pass

        # actualizar cupo tras cargar datos personales
        try:
            self._actualizar_cupo_disponible()
        except Exception:
            pass

        self.show_info("Datos cargados", f"Datos de {registro.get('nombre')} {registro.get('apellido')} cargados.\nSelecciona nueva materia para reinscribir.")

    def _eliminar_seleccionado(self):
        """Elimina el/los registro(s) seleccionado(s), guarda localmente y sincroniza SÍNCRONAMENTE con Google Sheets."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Eliminar", "Selecciona al menos un registro")
            return

        count = len(selection)
        if not self.ask_yes_no("Confirmar eliminación", f"¿Estás seguro de eliminar {count} inscripción(es)?"):
            return

        # Resolver IDs completos a partir de la selección (usar id_map/_get_id_from_item para mayor fiabilidad)
        try:
            registros = cargar_registros()
        except Exception:
            registros = []

        full_ids_to_delete = []
        registros_eliminados = []

        for iid in list(selection):
            try:
                reg_id = self._get_id_from_item(iid)
            except Exception:
                reg_id = ""

            if not reg_id:
                try:
                    vals = self.tree.item(iid).get("values") or []
                    reg_id = str(vals[0]) if vals else ""
                except Exception:
                    reg_id = ""

            matched_full = None
            for reg in registros:
                rid = str(reg.get("id", "") or "")
                if not rid:
                    continue
                if rid == reg_id or (reg_id and rid.startswith(reg_id)):
                    matched_full = rid
                    registros_eliminados.append(reg)
                    break

            if matched_full:
                full_ids_to_delete.append(matched_full)
            else:
                if reg_id:
                    full_ids_to_delete.append(reg_id)
                else:
                    print(f"[WARN] _eliminar_seleccionado: No pude determinar ID para item {iid}")

        print("[DEBUG] _eliminar_seleccionado: full_ids_to_delete:", full_ids_to_delete)
        print("[DEBUG] _eliminar_seleccionado: registros_eliminados_count:", len(registros_eliminados))

        if not full_ids_to_delete:
            self.show_warning("Eliminar", "No se pudieron determinar los IDs a eliminar")
            return

        # 3) Borrar filas de la UI inmediatamente para dar feedback
        for iid in list(selection):
            try:
                if hasattr(self, "id_map") and iid in self.id_map:
                    try:
                        del self.id_map[iid]
                    except Exception:
                        pass
                self.tree.delete(iid)
            except Exception:
                pass

        # 4) Filtrar registros locales y guardar el CSV (atomic write)
        registros_actuales = cargar_registros()
        def deberia_eliminar(r):
            rid = str(r.get("id", "") or "")
            for fid in full_ids_to_delete:
                if not fid:
                    continue
                if rid == fid or rid.startswith(str(fid)):
                    return True
            return False

        registros_filtrados = [r for r in registros_actuales if not deberia_eliminar(r)]

        from database.csv_handler import guardar_todos_registros
        print("[DEBUG] eliminar_seleccionado: registros antes:", len(registros_actuales), "después:", len(registros_filtrados))
        ok, msg = guardar_todos_registros(registros_filtrados)
        print("[DEBUG] guardar_todos_registros ->", ok, msg)
        if not ok:
            self.show_error("Error", f"No se pudo actualizar el archivo local: {msg}")
            self.refresh()
            return

        # ==== SINCRONIZACIÓN SÍNCRONA (delete por ID + push completo + verify + retry) ====
        try:
            sheet_key = settings.get("google_sheets.sheet_key", "") or settings.get("spreadsheet_id", "") or settings.get("sheet_key", "")
        except Exception:
            sheet_key = ""

        if sheet_key:
            try:
                from services.google_sheets import delete_row_by_id, sync_to_google_sheets, verify_remote_sync
                import time
                # 1) delete por ID (intentar para cada id)
                for reg in registros_eliminados:
                    idv = str(reg.get("id", "") or "")
                    if not idv:
                        continue
                    try:
                        okd, msgd = delete_row_by_id(sheet_key, idv)
                        print(f"[INFO] delete_row_by_id id={idv} ->", okd, msgd)
                    except Exception as e:
                        print(f"[WARN] delete_row_by_id exception id={idv}:", e)

                # 2) push completo sincronizado
                ok_push, msg_push = sync_to_google_sheets(sheet_key)
                print("[DEBUG] _eliminar_seleccionado: sync_to_google_sheets ->", ok_push, msg_push)

                # 3) verify readback
                ok_v, values = verify_remote_sync(sheet_key)
                if ok_v:
                    remote_rows = max(0, len(values) - 1) if len(values) > 0 else 0
                    local_rows = len(cargar_registros())
                    print(f"[DEBUG] _eliminar_seleccionado: verify -> remote_rows={remote_rows} local_rows={local_rows}")
                    if remote_rows != local_rows:
                        # retry one time
                        print("[DEBUG] _eliminar_seleccionado: mismatch counts, retrying push once...")
                        time.sleep(1)
                        ok_push2, msg_push2 = sync_to_google_sheets(sheet_key)
                        print("[DEBUG] _eliminar_seleccionado: retry sync ->", ok_push2, msg_push2)
                        ok_v2, values2 = verify_remote_sync(sheet_key)
                        if ok_v2:
                            remote_rows2 = max(0, len(values2) - 1) if len(values2) > 0 else 0
                            if remote_rows2 != local_rows:
                                self.show_warning("Sincronización parcial", f"Tras borrar, la hoja remota ({remote_rows2}) no coincide con el local ({local_rows}). Revisa permisos/otro equipo.")
                        else:
                            self.show_warning("Sincronización", f"Push realizado pero no se pudo verificar el resultado: {values2}")
                else:
                    print("[WARN] _eliminar_seleccionado: verify_remote_sync falló:", values)
                    self.show_warning("Sincronización", f"Push realizado pero no se pudo verificar el resultado: {values}")
            except Exception as e:
                print("[WARN] _eliminar_seleccionado: error sincronizando remoto:", e)
        else:
            print("[INFO] _eliminar_seleccionado: sheet_key no configurado; cambios guardados solo localmente")

        # 6) Mensaje al usuario y refresco de UI
        self.show_info("Eliminado", f"{len(full_ids_to_delete)} registro(s) eliminado(s) localmente. Sincronización finalizada.")
        try:
            self.refresh()
        except Exception:
            pass
        try:
            self.app.refresh_all()
        except Exception:
            pass

        # Lanzar una sola sincronización robusta en background: deletes puntuales + push completo
        def sync_worker(deleted_regs, updated_list):
            lock = getattr(self, "_sync_lock", None)
            if lock:
                lock.acquire()
            try:
                try:
                    sheet_key = settings.get("google_sheets.sheet_key", "") or settings.get("spreadsheet_id", "") or settings.get("sheet_key", "")
                except Exception:
                    sheet_key = ""

                if not sheet_key:
                    print("[INFO] sync_worker: No sheet_key configurado, no se sincroniza remotamente")
                    return

                # 1) Intentar delete por ID (services preferred)
                deleted_ids = [str(r.get("id", "")) for r in (deleted_regs or [])]
                print("[INFO] sync_worker: intentar deletes remotos para IDs:", deleted_ids)

                try:
                    from services.google_sheets import delete_row_by_id as svc_delete
                except Exception:
                    svc_delete = None

                for reg in (deleted_regs or []):
                    idv = str(reg.get("id", "") or "")
                    if not idv:
                        continue
                    try:
                        if svc_delete:
                            okd, msgd = svc_delete(sheet_key, idv)
                            print(f"[INFO] delete_row_by_id (services) id={idv} ->", okd, msgd)
                        else:
                            try:
                                from database.google_sheets import delete_row_by_id as db_delete
                                okd, msgd = db_delete(sheet_key, idv)
                                print(f"[INFO] delete_row_by_id (database) id={idv} ->", okd, msgd)
                            except Exception as e_db:
                                print(f"[WARN] No hay helper de delete disponible para id={idv}: {e_db}")
                    except Exception as e:
                        print(f"[WARN] Excepción al intentar borrar id={idv}:", e)

                # 2) Forzar push completo del CSV actualizado (remote <- local)
                try:
                    from database.google_sheets import subir_a_google_sheets
                    print("[INFO] sync_worker: forzando push completo del CSV actualizado (remote <- local), filas:", len(updated_list))
                    ok2, msg2 = subir_a_google_sheets(updated_list, sheet_key)
                    print("[INFO] push completo ->", ok2, msg2)
                    if not ok2:
                        print("[WARN] push completo devolvió fallo:", msg2)
                except Exception as e:
                    print("[ERROR] sync_worker: error al forzar push completo:", e)
            finally:
                if lock:
                    try:
                        lock.release()
                    except Exception:
                        pass

        threading.Thread(target=sync_worker, args=(registros_eliminados, registros_filtrados), daemon=True).start()

        # feedback y refrescos
        self.show_info("Eliminado", f"{len(full_ids_to_delete)} registro(s) eliminado(s) localmente. Sincronizando hoja remota...")
        try:
            self.refresh()
        except Exception:
            pass
        try:
            self.app.refresh_all()
        except Exception:
            pass

    def _enviar_certificado_seleccionado(self):
        """Genera y envía certificado del registro seleccionado en la tabla."""
        sel = self.tree.selection()
        if not sel:
            self.show_warning("Sin selección", "Selecciona un registro de la tabla")
            return

        item = self.tree.item(sel[0])
        values = item.get("values") or []
        if not values:
            return
        id_corto = str(values[0])

        # Buscar registro seleccionado de forma robusta (evita TypeError si id es int/None)
        registros = cargar_registros()
        registro = None
        for r in registros:
            try:
                rid = r.get("id", "")
            except Exception:
                rid = ""
            if rid is None:
                continue
            try:
                if str(rid).startswith(str(id_corto)):
                    registro = r
                    break
            except Exception:
                # si por algún motivo no se puede convertir/comparar, continuar con el siguiente registro
                continue

        if not registro:
            self.show_error("Error", "No se encontró el registro seleccionado")
            return

        if not registro.get("email"):
            self.show_warning("Sin email", f"{registro.get('nombre')} {registro.get('apellido')} no tiene email configurado")
            return

        ok, result = generar_certificado_pdf(registro)
        if not ok:
            self.show_error("Error al generar", result)
            return
        pdf_path = result

        smtp_cfg = get_smtp_config()
        if not smtp_cfg.get("username") or not smtp_cfg.get("password"):
            self.show_warning("SMTP no configurado", "Configurá SMTP en la pestaña Configuración")
            return

        def worker():
            ok_email, msg = send_certificado_via_email(registro, pdf_path, smtp_cfg)
            def finish():
                if ok_email:
                    self.show_info("Email enviado", msg)
                else:
                    self.show_error("Error al enviar", msg)
            try:
                self.app.root.after(1, finish)
            except Exception:
                finish()

        threading.Thread(target=worker, daemon=True).start()
        self.show_info("Envío en background", f"Enviando certificado de {registro.get('nombre')} {registro.get('apellido')}")

        def worker():
            ok_email, msg = send_certificado_via_email(registro, pdf_path, smtp_cfg)
            def finish():
                if ok_email:
                    self.show_info("Email enviado", msg)
                else:
                    self.show_error("Error al enviar", msg)
            try:
                self.app.root.after(1, finish)
            except Exception:
                finish()

        threading.Thread(target=worker, daemon=True).start()
        self.show_info("Envío en background", f"Enviando certificado de {registro.get('nombre')} {registro.get('apellido')}")

    def refresh(self):
        """Refresca la tabla con los registros guardados."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        registros = cargar_registros()
        self.id_map = {}
        for idx, reg in enumerate(registros):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            id_display = str(reg.get("id", ""))[:8]
            item_id = self.tree.insert("", tk.END, values=(
                id_display,
                reg.get("nombre", ""),
                reg.get("apellido", ""),
                reg.get("dni", ""),
                reg.get("materia", ""),
                reg.get("profesor", ""),
                reg.get("turno", ""),
                reg.get("anio", "")
            ), tags=(tag,))
            self.id_map[item_id] = str(reg.get("id", ""))

        # actualizar cupo al refrescar lista
        try:
            self._actualizar_cupo_disponible()
        except Exception:
            pass

    def _on_anio_change(self, event=None):
        """Al cambiar año, cargar las materias disponibles y limpiar selects dependientes."""
        try:
            anio = (self.anio_var.get() or "").strip()
        except Exception:
            anio = ""

        if not anio:
            # limpiar dependientes
            try:
                self.materia_combo['values'] = []
                self.materia_var.set("")
            except Exception:
                pass
            try:
                if hasattr(self, "profesor_var"):
                    self.profesor_var.set("")
                if hasattr(self, "comision_var"):
                    self.comision_var.set("")
                if hasattr(self, "horario_var"):
                    self.horario_var.set("")
            except Exception:
                pass
            # actualizar cupo
            try:
                self._actualizar_cupo_disponible()
            except Exception:
                pass
            return

        try:
            materias = get_materias_por_anio(int(anio))
        except Exception:
            materias = []

        try:
            self.materia_combo['values'] = materias
        except Exception:
            pass

        # limpiar selecciónes dependientes
        try:
            self.materia_var.set("")
            if hasattr(self, "profesor_var"):
                self.profesor_var.set("")
            if hasattr(self, "comision_var"):
                self.comision_var.set("")
            if hasattr(self, "horario_var"):
                self.horario_var.set("")
        except Exception:
            pass

        # actualizar cupo
        try:
            self._actualizar_cupo_disponible()
        except Exception:
            pass


    def _on_materia_change(self, event=None):
        """Al cambiar materia, cargar profesores y limpiar comisiones/horario."""
        try:
            materia = (self.materia_var.get() or "").strip()
        except Exception:
            materia = ""

        if not materia:
            try:
                self.profesor_combo['values'] = []
                self.profesor_var.set("")
                self.comision_combo['values'] = []
                self.comision_var.set("")
                if hasattr(self, "horario_var"):
                    self.horario_var.set("")
            except Exception:
                pass
            # actualizar cupo
            try:
                self._actualizar_cupo_disponible()
            except Exception:
                pass
            return

        try:
            anio = (self.anio_var.get() or "").strip()
            profesores = get_profesores_materia(materia, int(anio) if anio else None) or []
        except Exception:
            profesores = []

        try:
            self.profesor_combo['values'] = profesores
        except Exception:
            pass

        # limpiar dependientes
        try:
            self.profesor_var.set("")
            self.comision_combo['values'] = []
            self.comision_var.set("")
            if hasattr(self, "horario_var"):
                self.horario_var.set("")
        except Exception:
            pass

        # actualizar cupo
        try:
            self._actualizar_cupo_disponible()
        except Exception:
            pass


    def _on_profesor_change(self, event=None):
        """Al cambiar profesor, cargar comisiones y limpiar horario."""
        try:
            materia = (self.materia_var.get() or "").strip()
            profesor = (self.profesor_var.get() or "").strip()
        except Exception:
            materia = profesor = ""

        if not materia or not profesor:
            try:
                self.comision_combo['values'] = []
                self.comision_var.set("")
                if hasattr(self, "horario_var"):
                    self.horario_var.set("")
            except Exception:
                pass
            # actualizar cupo
            try:
                self._actualizar_cupo_disponible()
            except Exception:
                pass
            return

        try:
            anio = (self.anio_var.get() or "").strip()
            comisiones = get_comisiones_profesor(materia, profesor, int(anio) if anio else None) or []
        except Exception:
            comisiones = []

        try:
            # Si la lista contiene solo cadena vacía, dejamos el combo con un valor vacío
            # para permitir seleccionar profesor en materias sin comisiones.
            self.comision_combo['values'] = comisiones
        except Exception:
            pass

        try:
            # Resetear selección de comisión y horario al cambiar profesor
            self.comision_var.set("")
            if hasattr(self, "horario_var"):
                self.horario_var.set("")
        except Exception:
            pass

        # actualizar cupo
        try:
            self._actualizar_cupo_disponible()
        except Exception:
            pass


    def _on_comision_change(self, event=None):
        """Al cambiar comisión, obtener horario y actualizar cupo si aplica."""
        try:
            materia = (self.materia_var.get() or "").strip()
            profesor = (self.profesor_var.get() or "").strip()
            comision = (self.comision_var.get() or "").strip()
        except Exception:
            materia = profesor = comision = ""

        if not (materia and profesor and comision):
            try:
                if hasattr(self, "horario_var"):
                    self.horario_var.set("Sin horario")
            except Exception:
                pass
            # intentar actualizar cupo aunque falte data
            try:
                if hasattr(self, "_actualizar_cupo_disponible"):
                    self._actualizar_cupo_disponible()
            except Exception:
                pass
            return

        horario = None
        try:
            horario = get_horario(materia, profesor, comision)
        except Exception:
            horario = None

        try:
            if horario:
                self.horario_var.set(horario)
            else:
                # fallback a texto por defecto
                self.horario_var.set("Sin horario")
        except Exception:
            pass

        # actualizar label de cupo si existe
        try:
            if hasattr(self, "_actualizar_cupo_disponible"):
                self._actualizar_cupo_disponible()
        except Exception:
            pass

    def _guardar(self):
        """Guarda la inscripción (validaciones mínimas + guardado + sincronización SÍNCRONA con Google Sheets)."""
        # Validar campos obligatorios
        if not self.entries.get("nombre") or not self.entries["nombre"].get().strip():
            self.show_warning("Validación", "El nombre es obligatorio")
            return

        if not self.entries.get("apellido") or not self.entries["apellido"].get().strip():
            self.show_warning("Validación", "El apellido es obligatorio")
            return

        if not self.entries.get("dni") or not self.entries["dni"].get().strip():
            self.show_warning("Validación", "El DNI es obligatorio")
            return

        if not (hasattr(self, "anio_var") and self.anio_var.get()):
            self.show_warning("Validación", "El año es obligatorio")
            return

        if not (hasattr(self, "materia_var") and self.materia_var.get()):
            self.show_warning("Validación", "La materia es obligatoria")
            return

        if not (hasattr(self, "profesor_var") and self.profesor_var.get()):
            self.show_warning("Validación", "El profesor es obligatorio")
            return

        if not (hasattr(self, "comision_var") and self.comision_var.get()):
            self.show_warning("Validación", "La comisión es obligatoria")
            return

        # Generar ID
        nuevo_id = None
        try:
            nuevo_id = generar_id({
                "legajo": (self.entries.get("legajo") and self.entries["legajo"].get().strip()) or "",
                "dni": (self.entries.get("dni") and self.entries["dni"].get().strip()) or ""
            })
            if not nuevo_id:
                raise Exception("generar_id devolvió vacío")
        except Exception:
            import uuid
            nuevo_id = str(uuid.uuid4())

        # Limpiar valores de anio y turno antes de guardar
        # Extraer solo el número del año
        año_raw = self.anio_var.get() if hasattr(self, "anio_var") else ""
        año_limpio = ""
        if año_raw:
            # Si viene "Año: 1°" o "1°" -> extraer solo el "1"
            match = re.search(r'\d+', año_raw)
            if match:
                año_limpio = match.group(0)  # Solo el número

        # Limpiar el turno (eliminar "Año: " y "°")
        turno_raw = self.turno_var.get() if hasattr(self, "turno_var") else ""
        turno_limpio = turno_raw
        if "Año:" in turno_limpio:
            turno_limpio = ""  # Si viene con "Año:" es que está mal, vaciar
        elif "°" in turno_limpio:
            turno_limpio = turno_limpio.replace("°", "").strip()

        # Construir registro
        registro = {
            "id": str(nuevo_id),
            "fecha_inscripcion": datetime.now().isoformat(),
            "nombre": (self.entries.get("nombre") and self.entries["nombre"].get().strip()) or "",
            "apellido": (self.entries.get("apellido") and self.entries["apellido"].get().strip()) or "",
            "dni": (self.entries.get("dni") and self.entries["dni"].get().strip()) or "",
            "fecha_nacimiento": (self.entries.get("fecha_nacimiento") and self.entries["fecha_nacimiento"].get().strip()) or "",
            "edad": (self.entries.get("edad") and self.entries["edad"].get().strip()) or "",
            "legajo": (self.entries.get("legajo") and self.entries["legajo"].get().strip()) or "",
            "direccion": (self.entries.get("direccion") and self.entries["direccion"].get().strip()) or "",
            "telefono": (self.entries.get("telefono") and self.entries["telefono"].get().strip()) or "",
            "email": (self.entries.get("email") and self.entries["email"].get().strip()) or "",
            "nombre_padre": (self.entries.get("nombre_padre") and self.entries["nombre_padre"].get().strip()) or "",
            "nombre_madre": (self.entries.get("nombre_madre") and self.entries["nombre_madre"].get().strip()) or "",
            "telefono_emergencia": (self.entries.get("telefono_emergencia") and self.entries["telefono_emergencia"].get().strip()) or "",
            "saeta": (self.saeta_var.get() if hasattr(self, "saeta_var") else "No"),
            "obra_social": (self.entries.get("obra_social") and self.entries["obra_social"].get().strip()) or "",
            "seguro_escolar": (self.seguro_escolar_var.get() if hasattr(self, "seguro_escolar_var") else "No"),
            "pago_voluntario": (self.pago_voluntario_var.get() if hasattr(self, "pago_voluntario_var") else "No"),
            "monto": (self.entries.get("monto") and self.entries["monto"].get().strip()) or "",
            "permiso": (self.permiso_var.get() if hasattr(self, "permiso_var") else "No"),
            "anio": año_limpio,
            "turno": turno_limpio,
            "materia": (self.materia_var.get() if hasattr(self, "materia_var") else ""),
            "profesor": (self.profesor_var.get() if hasattr(self, "profesor_var") else ""),
            "comision": (self.comision_var.get() if hasattr(self, "comision_var") else ""),
            "horario": (self.horario_var.get() if hasattr(self, "horario_var") else ""),
            "observaciones": (self.observaciones_text.get("1.0", tk.END).strip() if hasattr(self, "observaciones_text") else ""),
            "en_lista_espera": "No"
        }

        # ===== Verificar cupo antes de guardar =====
        try:
            materia = registro.get("materia", "")
            profesor = registro.get("profesor", "")
            comision = registro.get("comision", "")
            cupo_val = None
            inscritos = 0

            # intentar obtener cupo por materia/profesor/comision desde instruments (get_info_completa)
            try:
                info = get_info_completa(materia, profesor, comision)
                if info and ("cupo" in info and info.get("cupo") is not None):
                    try:
                        cupo_val = int(info.get("cupo"))
                    except Exception:
                        cupo_val = None
            except Exception:
                info = None

            # contar inscritos (filtrado por materia/profesor/comision si es posible)
            try:
                inscritos = contar_inscripciones_materia(materia, profesor if profesor else None, comision if comision else None)
            except Exception:
                inscritos = 0

            restante = None if cupo_val is None else max(0, cupo_val - inscritos)

            # si cupo definido y completo -> preguntar lista de espera
            if cupo_val is not None and restante <= 0:
                if not self.ask_yes_no("Cupo completo", f"No quedan vacantes en {materia} / com. {comision}. Desea inscribir en lista de espera?"):
                    # usuario canceló, abortar guardado
                    self.show_info("Cancelado", "Inscripción cancelada por el usuario.")
                    return
                else:
                    registro["en_lista_espera"] = "Sí"
                    # agregar observación automática si no existe
                    obs = registro.get("observaciones", "") or ""
                    if "Lista de espera" not in obs:
                        registro["observaciones"] = (obs + " | Inscrito en lista de espera").strip().lstrip("|").strip()
        except Exception as e:
            print("[WARN] error verificando cupo:", e)

        # Guardar localmente
        try:
            ok_local, msg_local = guardar_registro(registro)
        except Exception as e:
            self.show_error("Error", f"No se pudo guardar: {e}")
            return

        print("[DEBUG] _guardar: guardado local ok:", ok_local, "msg:", msg_local, "id:", registro.get("id"))

        # Preparar sheet_key
        try:
            sheet_key = settings.get("google_sheets.sheet_key", "") or settings.get("spreadsheet_id", "")
        except Exception:
            sheet_key = ""

        print("[DEBUG] _guardar: sheet_key actual:", sheet_key)

        # Si hay sheet_key, hacer push SÍNCRONO + readback + retry 1 vez
        if sheet_key:
            try:
                from services.google_sheets import sync_to_google_sheets, verify_remote_sync
                import time, json
                # intento 1
                ok_push, msg_push = sync_to_google_sheets(sheet_key)
                print("[DEBUG] _guardar: sync_to_google_sheets ->", ok_push, msg_push)

                # readback para verificar conteo (header + rows)
                ok_v, values = verify_remote_sync(sheet_key)
                if ok_v:
                    # calcular filas de datos leídas (excluir header si existe)
                    remote_rows = max(0, len(values) - 1) if len(values) > 0 else 0
                    from database.csv_handler import cargar_registros
                    local_rows = len(cargar_registros())
                    print(f"[DEBUG] _guardar: verify_remote_sync -> remote_rows={remote_rows} local_rows={local_rows}")
                    if remote_rows != local_rows:
                        # retry una vez
                        print("[DEBUG] _guardar: mismatch counts, reintentando push completo (retry 1)...")
                        time.sleep(1)
                        ok_push2, msg_push2 = sync_to_google_sheets(sheet_key)
                        print("[DEBUG] _guardar: retry sync_to_google_sheets ->", ok_push2, msg_push2)
                        ok_v2, values2 = verify_remote_sync(sheet_key)
                        if ok_v2:
                            remote_rows2 = max(0, len(values2) - 1) if len(values2) > 0 else 0
                            print(f"[DEBUG] _guardar: post-retry remote_rows={remote_rows2}")
                            if remote_rows2 != local_rows:
                                self.show_warning("Sincronización parcial", f"Se intentó sincronizar, pero las filas remotas ({remote_rows2}) no coinciden con las locales ({local_rows}). Revisa conexión/permisos.")
                        else:
                            self.show_warning("Sincronización", f"Push realizado pero no se pudo verificar el resultado: {values2}")
                else:
                    print("[WARN] _guardar: verify_remote_sync falló:", values)
                    self.show_warning("Sincronización", f"Push realizado pero no se pudo verificar el resultado: {values}")
            except Exception as e:
                print("[WARN] _guardar: error al sincronizar:", e)
                # No bloquear al usuario por un fallo de red; ya guardamos localmente
        else:
            print("[INFO] _guardar: sheet_key no configurado; guardado local finalizado (sin sincronizar remoto)")

        # Feedback al usuario y refresco UI
        try:
            self.show_info("Éxito", f"Inscripción guardada correctamente\nID: {str(nuevo_id)[:8]}")
        except Exception:
            print("[INFO] Inscripción guardada, ID:", str(nuevo_id)[:8])

        try:
            self._limpiar()
        except Exception as e:
            print(f"[WARN] _guardar: Error al limpiar formulario: {e}")
        try:
            self.refresh()
        except Exception as e:
            print(f"[WARN] _guardar: Error al refrescar tabla: {e}")
        try:
            # Actualizar cupo disponible después de guardar
            self._actualizar_cupo_disponible()
        except Exception as e:
            print(f"[WARN] _guardar: Error al actualizar cupo: {e}")
        try:
            self.app.refresh_all()
        except Exception as e:
            print(f"[WARN] _guardar: Error al refrescar aplicación: {e}")
            
    def _limpiar(self):
        """Limpia todos los campos del formulario de forma robusta."""
        # Limpiar entradas del diccionario self.entries
        try:
            for key, entry in (self.entries or {}).items():
                try:
                    entry.delete(0, tk.END)
                except Exception:
                    # algunos elementos pueden no ser Entry en algunas versiones
                    try:
                        if hasattr(entry, "delete"):
                            entry.delete(0, tk.END)
                    except Exception:
                        pass
        except Exception:
            pass

        # Variables tipo combobox / flags
        try:
            if hasattr(self, "saeta_var"):
                self.saeta_var.set("No")
        except Exception:
            pass
        try:
            if hasattr(self, "seguro_escolar_var"):
                self.seguro_escolar_var.set("No")
        except Exception:
            pass
        try:
            if hasattr(self, "pago_voluntario_var"):
                self.pago_voluntario_var.set("No")
        except Exception:
            pass
        try:
            if hasattr(self, "permiso_var"):
                self.permiso_var.set("No")
        except Exception:
            pass

        # Campos de materia / turno
        try:
            if hasattr(self, "anio_var"):
                self.anio_var.set("")
        except Exception:
            pass
        try:
            if hasattr(self, "turno_var"):
                self.turno_var.set("")
        except Exception:
            pass
        try:
            if hasattr(self, "materia_var"):
                self.materia_var.set("")
        except Exception:
            pass
        try:
            if hasattr(self, "profesor_var"):
                self.profesor_var.set("")
        except Exception:
            pass
        try:
            if hasattr(self, "comision_var"):
                self.comision_var.set("")
        except Exception:
            pass
        try:
            if hasattr(self, "horario_var"):
                self.horario_var.set("")
        except Exception:
            pass

        # Observaciones (Text widget)
        try:
            if hasattr(self, "observaciones_text") and self.observaciones_text:
                self.observaciones_text.delete("1.0", tk.END)
        except Exception:
            pass

        # Label de cupo (si existe)
        try:
            if hasattr(self, "cupo_label"):
                self.cupo_label.config(text="Sin cupo definido", foreground="green")
        except Exception:
            pass

        # Opcional: deseleccionar cualquier fila en la tabla
        try:
            if hasattr(self, "tree"):
                self.tree.selection_remove(self.tree.selection())
        except Exception:
            pass

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

    def _generar_certificado_seleccionado(self):
        """Genera el certificado del registro seleccionado (sin enviarlo)."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Certificado", "Selecciona un registro de la tabla")
            return

        # Tomar la primera selección (la UI original usaba edición por 1)
        item = self.tree.item(selection[0])
        values = item.get("values") or []
        if not values:
            self.show_warning("Certificado", "El item seleccionado no tiene valores")
            return

        id_corto = str(values[0])

        # Buscar el registro completo en el CSV local
        registros = cargar_registros()
        registro = next((reg for reg in registros if str(reg.get("id", "")).startswith(id_corto)), None)
        if not registro:
            self.show_error("Error", "No se encontró el registro seleccionado")
            return

        try:
            ok, result = generar_certificado_pdf(registro)
            if ok:
                # result suele ser la ruta al PDF o mensaje de éxito
                self.show_info("Certificado", f"Certificado generado: {result}")
                # intentar abrir el PDF si se desea
                try:
                    path = str(result)
                    if path:
                        if sys.platform.startswith("darwin"):
                            os.system(f"open '{path}'")
                        elif os.name == "nt":
                            os.startfile(path)
                        else:
                            os.system(f"xdg-open '{path}'")
                except Exception:
                    pass
            else:
                self.show_error("Error al generar", result)
        except Exception as e:
            self.show_error("Error", f"Ocurrió un error al generar el certificado: {e}")

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

    def _enviar_certificado_seleccionado(self):
        """Genera y envía certificado del registro seleccionado en la tabla."""
        # Obtener selección
        sel = self.tree.selection()
        if not sel:
            self.show_warning("Sin selección", "Selecciona un registro de la tabla")
            return
        
        iid = sel[0]
        item = self.tree.item(iid)
        values = item['values']
        id_corto = values[0]
        
        # Buscar registro completo
        registros = cargar_registros()
        registro = None
        for r in registros:
            if r.get("id", "").startswith(id_corto):
                registro = r
                break
        
        if not registro:
            self.show_error("Error", "No se encontró el registro seleccionado")
            return
        
        # Validar email
        if not registro.get("email"):
            self.show_warning("Sin email", 
                             f"{registro.get('nombre')} {registro.get('apellido')} no tiene email configurado")
            return
        
        # Generar PDF
        ok, result = generar_certificado_pdf(registro)
        if not ok:
            self.show_error("Error al generar", result)
            return
        
        pdf_path = result
        
        # Obtener config SMTP
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
                       f"Enviando certificado de {registro.get('nombre')} {registro.get('apellido')}")

    def _sincronizar(self):
        """Sincronización bidireccional con Google Sheets (mismo comportamiento que en ConfigTab)."""
        # Intentar obtener sheet_key desde settings
        sheet_key = ""
        try:
            sheet_key = settings.get("google_sheets.sheet_key", "") or settings.get("spreadsheet_id", "") or settings.get("sheet_key", "")
        except Exception:
            sheet_key = ""

        if not sheet_key:
            self.show_warning("Google Sheets", "Ingresá el ID de la hoja en la pestaña Configuración primero.")
            return

        # Ejecutar en background
        def worker():
            from database.google_sheets import sincronizar_bidireccional
            try:
                ok, msg = sincronizar_bidireccional(sheet_key)
            except Exception as e:
                ok = False
                msg = f"Error sincronizando: {e}"

            def finish():
                if ok:
                    self.show_info("Sincronización exitosa", msg)
                    try:
                        self.app.refresh_all()
                    except:
                        pass
                else:
                    self.show_error("Error de sincronización", msg)

            try:
                self.frame.after(1, finish)
            except Exception:
                finish()

        threading.Thread(target=worker, daemon=True).start()
        self.show_info("Google Sheets", "Sincronizando bidireccionalmente en segundo plano...")

    # ================== MÉTODO NUEVO: actualizar cupo ==================
    def _actualizar_cupo_disponible(self):
        """
        Actualiza la etiqueta de cupo según:
          - info detallada por materia/profesor/comisión (instruments.json -> get_info_completa)
          - fallback a cupos.yaml usando calcular_cupos_restantes()
        """
        try:
            materia = (self.materia_var.get() if hasattr(self, "materia_var") else "") or ""
            profesor = (self.profesor_var.get() if hasattr(self, "profesor_var") else "") or ""
            comision = (self.comision_var.get() if hasattr(self, "comision_var") else "") or ""
        except Exception:
            materia = profesor = comision = ""

        # Si no hay materia seleccionada -> indicar sin cupo definido
        if not materia:
            try:
                self.cupo_label.config(text="Sin cupo definido", foreground="green")
            except Exception:
                pass
            return

        cupo_val = None
        inscritos = 0

        # 1) intentar obtener info completa desde models.materias (más granular)
        try:
            info = get_info_completa(materia, profesor, comision)
            if info and ("cupo" in info and info.get("cupo") is not None):
                try:
                    cupo_val = int(info.get("cupo"))
                except Exception:
                    cupo_val = None
        except Exception:
            info = None

        # 2) contar inscritos (intentar filtrar por materia/profesor/comision si estan)
        try:
            inscritos = contar_inscripciones_materia(materia, profesor if profesor else None, comision if comision else None)
        except Exception:
            inscritos = 0

        restante = None if cupo_val is None else max(0, cupo_val - inscritos)

        # 3) Si no hay cupo detalle, intentar fallback a cupos.yaml mediante helper cupos.py
        if cupo_val is None:
            try:
                # importar helper de cupos desde services o root
                try:
                    from services.cupos import calcular_cupos_restantes
                except Exception:
                    from cupos import calcular_cupos_restantes
                ok, data = calcular_cupos_restantes()
                if ok and isinstance(data, dict) and materia in data:
                    entry = data.get(materia, {})
                    # entry puede ser dict con 'cupo' o valor simple
                    v = entry.get("cupo") if isinstance(entry, dict) and entry.get("cupo") is not None else entry if not isinstance(entry, dict) else None
                    if v is not None:
                        try:
                            cupo_val = int(v)
                            restante = max(0, cupo_val - inscritos)
                        except Exception:
                            cupo_val = None
                else:
                    cupo_val = None
            except Exception:
                cupo_val = None

        # 4) Actualizar label según lo obtenido
        try:
            if cupo_val is None:
                # cupo no definido
                self.cupo_label.config(text="Cupo no definido (libre)", foreground="orange")
            else:
                if restante <= 0:
                    self.cupo_label.config(text=f"Cupo agotado (0/{cupo_val})", foreground="red")
                else:
                    self.cupo_label.config(text=f"Disponibles: {restante} / {cupo_val}", foreground="green")
        except Exception:
            pass

        return cupo_val, inscritos, restante