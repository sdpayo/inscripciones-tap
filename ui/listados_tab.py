"""Pestaña de Listados y Reportes."""
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
from ui.base_tab import BaseTab
from database.csv_handler import cargar_registros, exportar_listado
from models.materias import get_todas_materias, get_profesores_materia
import csv
from pathlib import Path

class ListadosTab(BaseTab):
    """Pestaña para generar listados y reportes."""
    
    def _build_ui(self):
        """Construye la interfaz de listados."""
        # Dividir en dos secciones: filtros (arriba) + resultados (abajo)
        
        # === SECCIÓN FILTROS ===
        filtros_frame = ttk.LabelFrame(self.frame, text="Filtros", padding=10)
        filtros_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self._build_filtros(filtros_frame)
        
        # === SECCIÓN RESULTADOS ===
        resultados_frame = ttk.LabelFrame(self.frame, text="Resultados", padding=10)
        resultados_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self._build_resultados(resultados_frame)
        
        # === BOTONES DE ACCIÓN ===
        botones_frame = ttk.Frame(self.frame)
        botones_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self._build_botones(botones_frame)
    
    def _build_filtros(self, parent):
        """Construye sección de filtros."""
        # Grid layout para filtros
        row = 0
        
        # Filtro por Materia
        ttk.Label(parent, text="Materia:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.filtro_materia_var = tk.StringVar()
        materia_combo = ttk.Combobox(
            parent,
            textvariable=self.filtro_materia_var,
            values=["(Todas)"] + get_todas_materias(),
            state="readonly",
            width=40
        )
        materia_combo.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        materia_combo.set("(Todas)")
        materia_combo.bind("<<ComboboxSelected>>", self._on_filtro_materia_change)
        
        # Filtro por Profesor
        ttk.Label(parent, text="Profesor:").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.filtro_profesor_var = tk.StringVar()
        self.profesor_combo = ttk.Combobox(
            parent,
            textvariable=self.filtro_profesor_var,
            values=["(Todos)"],
            state="readonly",
            width=30
        )
        self.profesor_combo.grid(row=row, column=3, sticky="w", padx=5, pady=5)
        self.profesor_combo.set("(Todos)")
        
        row += 1
        
        # Filtro por Turno
        ttk.Label(parent, text="Turno:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.filtro_turno_var = tk.StringVar()
        turno_combo = ttk.Combobox(
            parent,
            textvariable=self.filtro_turno_var,
            values=["(Todos)", "Mañana", "Tarde", "Vespertino", "Noche"],
            state="readonly",
            width=15
        )
        turno_combo.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        turno_combo.set("(Todos)")
        
        # Filtro por Año
        ttk.Label(parent, text="Año:").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.filtro_anio_var = tk.StringVar()
        anio_combo = ttk.Combobox(
            parent,
            textvariable=self.filtro_anio_var,
            values=["(Todos)", "1", "2", "3", "4"],
            state="readonly",
            width=10
        )
        anio_combo.grid(row=row, column=3, sticky="w", padx=5, pady=5)
        anio_combo.set("(Todos)")
        
        row += 1
        
        # Botón aplicar filtros
        ttk.Button(
            parent,
            text="🔍 Aplicar Filtros",
            command=self._aplicar_filtros
        ).grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            parent,
            text="🔄 Limpiar Filtros",
            command=self._limpiar_filtros
        ).grid(row=row, column=2, columnspan=2, pady=10)
    
    def _build_resultados(self, parent):
        """Construye tabla de resultados."""
        # Frame para estadísticas
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_label = ttk.Label(
            stats_frame,
            text="Total: 0 inscripciones",
            font=("Helvetica", 10, "bold")
        )
        self.stats_label.pack(side=tk.LEFT)
        
        # Tabla con scrollbars
        table_container = ttk.Frame(parent)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(table_container, orient="vertical")
        hsb = ttk.Scrollbar(table_container, orient="horizontal")
        
        columns = ("nombre", "apellido", "dni", "materia", "profesor", "comision", "turno", "año")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configurar columnas
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellido", text="Apellido")
        self.tree.heading("dni", text="DNI")
        self.tree.heading("materia", text="Materia")
        self.tree.heading("profesor", text="Profesor")
        self.tree.heading("comision", text="Comisión")
        self.tree.heading("turno", text="Turno")
        self.tree.heading("año", text="Año")
        
        self.tree.column("nombre", width=120)
        self.tree.column("apellido", width=120)
        self.tree.column("dni", width=100)
        self.tree.column("materia", width=200)
        self.tree.column("profesor", width=150)
        self.tree.column("comision", width=80)
        self.tree.column("turno", width=100)
        self.tree.column("año", width=60)
        
        # Configurar tags para filas alternas
        self.tree.tag_configure("oddrow", background="#1E1E1E", foreground="#FFFFFF")
        self.tree.tag_configure("evenrow", background="#252525", foreground="#FFFFFF")
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
    
    def _build_botones(self, parent):
        """Construye botones de acción."""
        ttk.Button(
            parent,
            text="📄 Exportar a CSV",
            command=self._exportar_csv
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            parent,
            text="📊 Exportar a Excel",
            command=self._exportar_excel
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            parent,
            text="🖨️ Generar PDF",
            command=self._generar_pdf
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            parent,
            text="📈 Ver Estadísticas",
            command=self._ver_estadisticas
        ).pack(side=tk.LEFT, padx=5)
    
    # ========== HANDLERS ==========
    
    def _on_filtro_materia_change(self, event=None):
        """Al cambiar materia, actualizar profesores."""
        materia = self.filtro_materia_var.get()
        
        if materia == "(Todas)":
            self.profesor_combo['values'] = ["(Todos)"]
            self.filtro_profesor_var.set("(Todos)")
        else:
            profesores = get_profesores_materia(materia)
            self.profesor_combo['values'] = ["(Todos)"] + profesores
            self.filtro_profesor_var.set("(Todos)")
    
    def _aplicar_filtros(self):
        """Aplica filtros y actualiza tabla."""
        # Construir diccionario de filtros
        filtros = {}
        
        materia = self.filtro_materia_var.get()
        if materia and materia != "(Todas)":
            filtros["materia"] = materia
        
        profesor = self.filtro_profesor_var.get()
        if profesor and profesor != "(Todos)":
            filtros["profesor"] = profesor
        
        turno = self.filtro_turno_var.get()
        if turno and turno != "(Todos)":
            filtros["turno"] = turno
        
        anio = self.filtro_anio_var.get()
        if anio and anio != "(Todos)":
            filtros["anio"] = anio
        
        # Obtener registros filtrados
        registros = exportar_listado(filtros)
        self._actualizar_tabla(registros)
    
    def _limpiar_filtros(self):
        """Limpia todos los filtros."""
        self.filtro_materia_var.set("(Todas)")
        self.filtro_profesor_var.set("(Todos)")
        self.filtro_turno_var.set("(Todos)")
        self.filtro_anio_var.set("(Todos)")
        self.profesor_combo['values'] = ["(Todos)"]
        self._aplicar_filtros()
    
    def _actualizar_tabla(self, registros):
        """Actualiza tabla con registros."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Poblar tabla con filas alternas
        for idx, reg in enumerate(registros):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                tk.END,
                values=(
                    reg.get("nombre", ""),
                    reg.get("apellido", ""),
                    reg.get("dni", ""),
                    reg.get("materia", ""),
                    reg.get("profesor", ""),
                    reg.get("comision", ""),
                    reg.get("turno", ""),
                    reg.get("anio", "")
                ),
                tags=(tag,)
            )
        
        # Actualizar estadísticas
        self.stats_label.config(text=f"Total: {len(registros)} inscripciones")
        
        # Guardar para exportar
        self._registros_actuales = registros
    
    def _exportar_csv(self):
        """Exporta tabla actual a CSV."""
        if not hasattr(self, '_registros_actuales'):
            self.show_warning("Exportar", "Primero aplicá filtros.")
            return
        
        # Diálogo para guardar
        filename = filedialog.asksaveasfilename(
            title="Guardar CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"listado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            # Guardar CSV
            from config.settings import CSV_FIELDS
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
                writer.writeheader()
                writer.writerows(self._registros_actuales)
            
            self.show_info("Exportar", f"Exportado: {len(self._registros_actuales)} registros\n\n{filename}")
        except Exception as e:
            self.show_error("Error", f"No se pudo exportar: {e}")
    
    def _exportar_excel(self):
        """Exporta tabla actual a Excel."""
        if not hasattr(self, '_registros_actuales'):
            self.show_warning("Exportar", "Primero aplicá filtros.")
            return
        
        try:
            import openpyxl
        except ImportError:
            if self.ask_yes_no("openpyxl no instalado", "¿Instalar openpyxl para exportar a Excel?"):
                import subprocess
                subprocess.check_call(["pip", "install", "openpyxl"])
                import openpyxl
            else:
                return
        
        # Diálogo para guardar
        filename = filedialog.asksaveasfilename(
            title="Guardar Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"listado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        if not filename:
            return
        
        try:
            # Crear workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Inscripciones"
            
            # Headers
            from config.settings import CSV_FIELDS
            ws.append(CSV_FIELDS)
            
            # Datos
            for reg in self._registros_actuales:
                row = [reg.get(field, "") for field in CSV_FIELDS]
                ws.append(row)
            
            # Ajustar anchos
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column].width = adjusted_width
            
            # Guardar
            wb.save(filename)
            
            self.show_info("Exportar", f"Exportado: {len(self._registros_actuales)} registros\n\n{filename}")
        except Exception as e:
            self.show_error("Error", f"No se pudo exportar: {e}")
    
    def _generar_pdf(self):
        """Genera PDF del listado."""
        if not hasattr(self, '_registros_actuales'):
            self.show_warning("PDF", "Primero aplicá filtros.")
            return
        
        from services.pdf_generator import generar_listado_pdf
        
        # Diálogo para guardar
        filename = filedialog.asksaveasfilename(
            title="Guardar PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"listado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        if not filename:
            return
        
        try:
            ok, msg = generar_listado_pdf(self._registros_actuales, filename)
            if ok:
                self.show_info("PDF", msg)
            else:
                self.show_error("Error", msg)
        except Exception as e:
            self.show_error("Error", f"No se pudo generar PDF: {e}")
    
    def _ver_estadisticas(self):
        """Muestra ventana con estadísticas."""
        if not hasattr(self, '_registros_actuales'):
            self.show_warning("Estadísticas", "Primero aplicá filtros.")
            return
        
        # Calcular estadísticas
        total = len(self._registros_actuales)
        
        materias = {}
        profesores = {}
        turnos = {}
        anios = {}
        
        for reg in self._registros_actuales:
            # Por materia
            mat = reg.get("materia", "N/A")
            materias[mat] = materias.get(mat, 0) + 1
            
            # Por profesor
            prof = reg.get("profesor", "N/A")
            profesores[prof] = profesores.get(prof, 0) + 1
            
            # Por turno
            turno = reg.get("turno", "N/A")
            turnos[turno] = turnos.get(turno, 0) + 1
            
            # Por año
            anio = reg.get("anio", "N/A")
            anios[anio] = anios.get(anio, 0) + 1
        
        # Ventana de estadísticas
        stats_window = tk.Toplevel(self.frame)
        stats_window.title("Estadísticas")
        stats_window.geometry("600x500")
        
        # Notebook
        notebook = ttk.Notebook(stats_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña General
        general_frame = ttk.Frame(notebook, padding=10)
        notebook.add(general_frame, text="General")
        
        ttk.Label(
            general_frame,
            text=f"Total de Inscripciones: {total}",
            font=("Helvetica", 12, "bold")
        ).pack(pady=10)
        
        ttk.Label(general_frame, text=f"Materias distintas: {len(materias)}").pack(pady=5)
        ttk.Label(general_frame, text=f"Profesores distintos: {len(profesores)}").pack(pady=5)
        ttk.Label(general_frame, text=f"Turnos: {len(turnos)}").pack(pady=5)
        
        # Pestaña Por Materia
        self._crear_pestaña_stats(notebook, "Por Materia", materias)
        
        # Pestaña Por Profesor
        self._crear_pestaña_stats(notebook, "Por Profesor", profesores)
        
        # Pestaña Por Turno
        self._crear_pestaña_stats(notebook, "Por Turno", turnos)
        
        # Pestaña Por Año
        self._crear_pestaña_stats(notebook, "Por Año", anios)
    
    def _crear_pestaña_stats(self, notebook, titulo, datos):
        """Crea pestaña de estadísticas."""
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text=titulo)
        
        # Tabla
        tree = ttk.Treeview(frame, columns=("item", "cantidad"), show="headings", height=15)
        tree.heading("item", text=titulo.replace("Por ", ""))
        tree.heading("cantidad", text="Cantidad")
        
        tree.column("item", width=400)
        tree.column("cantidad", width=100)
        
        # Configurar tags para filas alternas
        tree.tag_configure("evenrow", background="#FFFFFF")
        tree.tag_configure("oddrow", background="#F8F9FA")
        
        # Poblar (ordenado por cantidad) con filas alternas
        for idx, (item, cantidad) in enumerate(sorted(datos.items(), key=lambda x: x[1], reverse=True)):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            tree.insert("", tk.END, values=(item, cantidad), tags=(tag,))
        
        tree.pack(fill=tk.BOTH, expand=True)
    
    def refresh(self):
        """Recarga datos."""
        self._aplicar_filtros()