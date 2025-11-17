"""Pestaña de Historial de Alumnos."""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ui.base_tab import BaseTab
from database.csv_handler import obtener_historial_alumno, buscar_por_dni, cargar_registros
from services.pdf_generator import generar_certificado_pdf

class HistorialTab(BaseTab):
    """Pestaña para consultar historial de alumnos."""
    
    def _build_ui(self):
        """Construye la interfaz de historial."""
        # Dividir en dos secciones: búsqueda (arriba) + resultados (abajo)
        
        # === SECCIÓN BÚSQUEDA ===
        busqueda_frame = ttk.LabelFrame(self.frame, text="Buscar Alumno", padding=10)
        busqueda_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self._build_busqueda(busqueda_frame)
        
        # === SECCIÓN RESULTADOS ===
        self.resultados_frame = ttk.Frame(self.frame)
        self.resultados_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Mensaje inicial
        self.mensaje_inicial = ttk.Label(
            self.resultados_frame,
            text="Buscá un alumno por DNI o nombre para ver su historial",
            font=("Helvetica", 11),
            foreground="gray"
        )
        self.mensaje_inicial.pack(expand=True)
    
    def _build_busqueda(self, parent):
        """Construye sección de búsqueda."""
        # Frame para campos de búsqueda
        campos_frame = ttk.Frame(parent)
        campos_frame.pack(fill=tk.X)
        
        # Búsqueda por DNI
        ttk.Label(campos_frame, text="DNI:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.dni_var = tk.StringVar()
        dni_entry = ttk.Entry(campos_frame, textvariable=self.dni_var, width=15)
        dni_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        dni_entry.bind("<Return>", lambda e: self._buscar())
        
        # Búsqueda por Nombre/Apellido
        ttk.Label(campos_frame, text="Nombre/Apellido:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.nombre_var = tk.StringVar()
        nombre_entry = ttk.Entry(campos_frame, textvariable=self.nombre_var, width=30)
        nombre_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        nombre_entry.bind("<Return>", lambda e: self._buscar())
        
        # Botones
        ttk.Button(
            campos_frame,
            text="🔍 Buscar",
            command=self._buscar
        ).grid(row=0, column=4, padx=10, pady=5)
        
        ttk.Button(
            campos_frame,
            text="🔄 Limpiar",
            command=self._limpiar_busqueda
        ).grid(row=0, column=5, padx=5, pady=5)
    
    def _buscar(self):
        """Busca alumno y muestra historial."""
        dni = self.dni_var.get().strip()
        nombre = self.nombre_var.get().strip().lower()
        
        if not dni and not nombre:
            self.show_warning("Búsqueda", "Ingresá DNI o nombre para buscar.")
            return
        
        # Buscar registros
        if dni:
            registros = buscar_por_dni(dni)
        else:
            # Buscar por nombre/apellido
            todos = cargar_registros()
            registros = [
                r for r in todos
                if nombre in r.get("nombre", "").lower() or nombre in r.get("apellido", "").lower()
            ]
        
        if not registros:
            self.show_info("Sin resultados", "No se encontraron registros para ese alumno.")
            self._limpiar_resultados()
            return
        
        # Mostrar resultados
        self._mostrar_historial(registros)
    
    def _mostrar_historial(self, registros):
        """Muestra historial del alumno."""
        # Limpiar resultados anteriores
        for widget in self.resultados_frame.winfo_children():
            widget.destroy()
        
        # === INFO DEL ALUMNO ===
        info_frame = ttk.Frame(self.resultados_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Datos del primer registro
        primer_reg = registros[0]
        nombre_completo = f"{primer_reg.get('nombre', '')} {primer_reg.get('apellido', '')}"
        dni = primer_reg.get("dni", "N/A")
        
        ttk.Label(
            info_frame,
            text=f"Alumno: {nombre_completo}",
            font=("Helvetica", 14, "bold")
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            info_frame,
            text=f"DNI: {dni}",
            font=("Helvetica", 12)
        ).pack(side=tk.LEFT, padx=20)
        
        ttk.Label(
            info_frame,
            text=f"Total inscripciones: {len(registros)}",
            font=("Helvetica", 12)
        ).pack(side=tk.LEFT, padx=20)
        
        # === ESTADÍSTICAS ===
        stats_frame = ttk.LabelFrame(self.resultados_frame, text="Resumen", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self._mostrar_estadisticas(stats_frame, registros)
        
        # === TABLA DE HISTORIAL ===
        tabla_frame = ttk.LabelFrame(self.resultados_frame, text="Historial de Inscripciones", padding=10)
        tabla_frame.pack(fill=tk.BOTH, expand=True)
        
        self._crear_tabla_historial(tabla_frame, registros)
    
    def _mostrar_estadisticas(self, parent, registros):
        """Muestra estadísticas del alumno."""
        # Calcular stats
        materias = set(r.get("materia", "") for r in registros)
        profesores = set(r.get("profesor", "") for r in registros)
        anios = set(r.get("anio", "") for r in registros)
        
        # Última inscripción
        registros_ordenados = sorted(
            registros,
            key=lambda x: x.get("fecha_inscripcion", ""),
            reverse=True
        )
        ultima_fecha = registros_ordenados[0].get("fecha_inscripcion", "N/A")
        ultima_materia = registros_ordenados[0].get("materia", "N/A")
        
        # Grid de stats
        row = 0
        
        ttk.Label(parent, text="Materias cursadas:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        ttk.Label(parent, text=str(len(materias)), font=("Helvetica", 10, "bold")).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        
        ttk.Label(parent, text="Profesores:").grid(row=row, column=2, sticky="e", padx=5, pady=3)
        ttk.Label(parent, text=str(len(profesores)), font=("Helvetica", 10, "bold")).grid(
            row=row, column=3, sticky="w", padx=5, pady=3
        )
        
        row += 1
        
        ttk.Label(parent, text="Años cursados:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        ttk.Label(parent, text=", ".join(sorted(str(a) for a in anios if a)), font=("Helvetica", 10, "bold")).grid(
            row=row, column=1, sticky="w", padx=5, pady=3
        )
        
        row += 1
        
        ttk.Label(parent, text="Última inscripción:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        ttk.Label(parent, text=f"{ultima_materia} ({ultima_fecha[:10]})", font=("Helvetica", 10, "bold")).grid(
            row=row, column=1, columnspan=3, sticky="w", padx=5, pady=3
        )
    
    def _crear_tabla_historial(self, parent, registros):
        """Crea tabla con historial."""
        # Scrollbars
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(container, orient="vertical")
        hsb = ttk.Scrollbar(container, orient="horizontal")
        
        # Treeview
        columns = ("fecha", "materia", "profesor", "comision", "turno", "año", "acciones")
        self.tree = ttk.Treeview(
            container,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configurar columnas
        self.tree.heading("fecha", text="Fecha Inscripción")
        self.tree.heading("materia", text="Materia")
        self.tree.heading("profesor", text="Profesor")
        self.tree.heading("comision", text="Comisión")
        self.tree.heading("turno", text="Turno")
        self.tree.heading("año", text="Año")
        self.tree.heading("acciones", text="")
        
        self.tree.column("fecha", width=120)
        self.tree.column("materia", width=250)
        self.tree.column("profesor", width=150)
        self.tree.column("comision", width=80)
        self.tree.column("turno", width=100)
        self.tree.column("año", width=60)
        self.tree.column("acciones", width=100)
        
        # Configurar tags para filas alternas
        self.tree.tag_configure("oddrow", background="#1E1E1E", foreground="#FFFFFF")
        self.tree.tag_configure("evenrow", background="#252525", foreground="#FFFFFF")
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Poblar tabla con filas alternas
        self._registros_historial = registros
        for idx, reg in enumerate(registros):
            fecha = reg.get("fecha_inscripcion", "N/A")[:10]
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                tk.END,
                values=(
                    fecha,
                    reg.get("materia", ""),
                    reg.get("profesor", ""),
                    reg.get("comision", ""),
                    reg.get("turno", ""),
                    reg.get("anio", ""),
                    "📄"  # Icono de certificado
                ),
                tags=(reg.get("id"), row_tag)
            )
        
        # Doble click para certificado
        self.tree.bind("<Double-1>", self._generar_certificado_seleccion)
        
        # Botones de acciones
        acciones_frame = ttk.Frame(parent)
        acciones_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            acciones_frame,
            text="📄 Generar Certificado",
            command=lambda: self._generar_certificado_seleccion(None)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            acciones_frame,
            text="📊 Exportar Historial",
            command=self._exportar_historial
        ).pack(side=tk.LEFT, padx=5)
    
    def _generar_certificado_seleccion(self, event):
        """Genera certificado del registro seleccionado."""
        selection = self.tree.selection()
        if not selection:
            self.show_warning("Certificado", "Seleccioná una inscripción.")
            return
        
        # Obtener ID del registro
        item = self.tree.item(selection[0])
        reg_id = item["tags"][0] if item["tags"] else None
        
        if not reg_id:
            self.show_error("Error", "No se pudo identificar el registro.")
            return
        
        # Buscar registro completo
        registro = None
        for reg in self._registros_historial:
            if reg.get("id") == reg_id:
                registro = reg
                break
        
        if not registro:
            self.show_error("Error", "Registro no encontrado.")
            return
        
        # Generar certificado
        try:
            ok, msg = generar_certificado_pdf(registro)
            if ok:
                self.show_info("Certificado", msg)
            else:
                self.show_error("Error", msg)
        except Exception as e:
            self.show_error("Error", f"No se pudo generar certificado: {e}")
    
    def _exportar_historial(self):
        """Exporta historial del alumno a CSV."""
        if not hasattr(self, '_registros_historial'):
            self.show_warning("Exportar", "Primero buscá un alumno.")
            return
        
        from tkinter import filedialog
        import csv
        
        # Nombre del alumno para el archivo
        primer_reg = self._registros_historial[0]
        nombre = primer_reg.get("nombre", "alumno")
        apellido = primer_reg.get("apellido", "")
        dni = primer_reg.get("dni", "")
        
        filename = filedialog.asksaveasfilename(
            title="Guardar Historial",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"historial_{apellido}_{nombre}_{dni}.csv"
        )
        
        if not filename:
            return
        
        try:
            from config.settings import CSV_FIELDS
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
                writer.writeheader()
                writer.writerows(self._registros_historial)
            
            self.show_info("Exportar", f"Historial exportado:\n{filename}")
        except Exception as e:
            self.show_error("Error", f"No se pudo exportar: {e}")
    
    def _limpiar_busqueda(self):
        """Limpia campos de búsqueda."""
        self.dni_var.set("")
        self.nombre_var.set("")
        self._limpiar_resultados()
    
    def _limpiar_resultados(self):
        """Limpia resultados mostrados."""
        for widget in self.resultados_frame.winfo_children():
            widget.destroy()
        
        self.mensaje_inicial = ttk.Label(
            self.resultados_frame,
            text="Buscá un alumno por DNI o nombre para ver su historial",
            font=("Helvetica", 11),
            foreground="gray"
        )
        self.mensaje_inicial.pack(expand=True)
    
    def refresh(self):
        """Refresca la pestaña."""
        # No hacer nada automáticamente (solo buscar cuando el usuario lo pida)
        pass