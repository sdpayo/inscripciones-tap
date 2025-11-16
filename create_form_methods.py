"""Crea todos los métodos _build_* faltantes en form_tab.py"""

# Código de los métodos a agregar
new_methods = '''
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

    def _build_otros_datos(self):
        """Construye sección de Otros Datos."""
        otros_frame = ttk.LabelFrame(self.form_container, text="Otros Datos", padding=10)
        otros_frame.pack(fill=tk.X, padx=10, pady=10)
        
        row = 0
        
        # SAETA
        ttk.Label(otros_frame, text="SAETA:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.saeta_var = tk.StringVar(value="No")
        ttk.Combobox(
            otros_frame,
            textvariable=self.saeta_var,
            values=["No", "Sí"],
            state="readonly",
            width=15
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        # Obra Social
        ttk.Label(otros_frame, text="Obra Social:").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.obra_social_var = tk.StringVar()
        ttk.Entry(otros_frame, textvariable=self.obra_social_var, width=30).grid(
            row=row, column=3, sticky="w", padx=5, pady=5
        )
        row += 1
        
        # Seguro Escolar
        ttk.Label(otros_frame, text="Seguro Escolar:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.seguro_escolar_var = tk.StringVar(value="No")
        ttk.Combobox(
            otros_frame,
            textvariable=self.seguro_escolar_var,
            values=["No", "Sí"],
            state="readonly",
            width=15
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        # Pago Voluntario
        ttk.Label(otros_frame, text="Pago Voluntario:").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.pago_voluntario_var = tk.StringVar(value="No")
        ttk.Combobox(
            otros_frame,
            textvariable=self.pago_voluntario_var,
            values=["No", "Sí"],
            state="readonly",
            width=15
        ).grid(row=row, column=3, sticky="w", padx=5, pady=5)
        row += 1
        
        # Monto
        ttk.Label(otros_frame, text="Monto:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.monto_var = tk.StringVar()
        ttk.Entry(otros_frame, textvariable=self.monto_var, width=15).grid(
            row=row, column=1, sticky="w", padx=5, pady=5
        )
        
        # Permiso
        ttk.Label(otros_frame, text="Permiso:").grid(row=row, column=2, sticky="e", padx=5, pady=5)
        self.permiso_var = tk.StringVar(value="No")
        ttk.Combobox(
            otros_frame,
            textvariable=self.permiso_var,
            values=["No", "Sí"],
            state="readonly",
            width=15
        ).grid(row=row, column=3, sticky="w", padx=5, pady=5)
        row += 1
        
        # Observaciones
        ttk.Label(otros_frame, text="Observaciones:").grid(row=row, column=0, sticky="ne", padx=5, pady=5)
        self.observaciones_text = tk.Text(otros_frame, width=60, height=4)
        self.observaciones_text.grid(row=row, column=1, columnspan=3, sticky="w", padx=5, pady=5)

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
        
        ttk.Label(
            inscripcion_frame,
            text="El horario se completa automáticamente",
            font=("Helvetica", 8),
            foreground="gray"
        ).grid(row=row+1, column=0, columnspan=4, sticky="w", padx=5)

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
'''

print("Leyendo form_tab.py...")
with open("ui/form_tab.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar dónde insertar (antes del método refresh o al final de la clase)
if '    def refresh(self):' in content:
    content = content.replace('    def refresh(self):', new_methods + '\n    def refresh(self):')
    print("✅ Métodos insertados antes de refresh()")
else:
    # Agregar al final de la clase
    # Buscar el último método
    import re
    # Buscar la última línea de un método de clase
    last_method = list(re.finditer(r'\n    def \w+\(self.*?\):', content))
    if last_method:
        # Insertar después del último método
        content += '\n' + new_methods
        print("✅ Métodos agregados al final de la clase")
    else:
        print("❌ No se pudo determinar dónde insertar")

# Guardar
with open("ui/form_tab.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ form_tab.py actualizado con todos los métodos")
print("\nAhora ejecutá: python main.py")