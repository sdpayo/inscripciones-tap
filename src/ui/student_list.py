"""Student list widget."""
import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable
from ..models import Student


class StudentList(ttk.Frame):
    """Widget for displaying a list of students."""
    
    def __init__(self, parent, on_select: Optional[Callable] = None):
        """
        Initialize student list.
        
        Args:
            parent: Parent widget
            on_select: Callback function when student is selected
        """
        super().__init__(parent)
        self.on_select = on_select
        self.students: List[Student] = []
        
        self.create_widget()
    
    def create_widget(self):
        """Create the treeview widget."""
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("nombre", "dni", "email", "telefono", "instrumento", "estado"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Define columns
        self.tree.heading("nombre", text="Nombre Completo")
        self.tree.heading("dni", text="DNI")
        self.tree.heading("email", text="Email")
        self.tree.heading("telefono", text="Teléfono")
        self.tree.heading("instrumento", text="Instrumento")
        self.tree.heading("estado", text="Estado")
        
        # Column widths
        self.tree.column("nombre", width=200)
        self.tree.column("dni", width=100)
        self.tree.column("email", width=200)
        self.tree.column("telefono", width=120)
        self.tree.column("instrumento", width=120)
        self.tree.column("estado", width=100)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_changed)
        
        # Add tags for status colors
        self.tree.tag_configure("Pendiente", background="#fff3cd")
        self.tree.tag_configure("Aprobado", background="#d4edda")
        self.tree.tag_configure("Rechazado", background="#f8d7da")
    
    def _on_selection_changed(self, event):
        """Handle selection change."""
        selected_items = self.tree.selection()
        if selected_items and self.on_select:
            item_id = selected_items[0]
            # Get student by index
            index = self.tree.index(item_id)
            if 0 <= index < len(self.students):
                self.on_select(self.students[index])
            else:
                self.on_select(None)
    
    def update_students(self, students: List[Student]):
        """
        Update the list of students displayed.
        
        Args:
            students: List of students to display
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Store students
        self.students = students
        
        # Add students to tree
        for student in students:
            values = (
                student.get_full_name(),
                student.dni,
                student.email,
                student.telefono,
                student.instrumento or "-",
                student.estado
            )
            self.tree.insert("", "end", values=values, tags=(student.estado,))
    
    def clear(self):
        """Clear all items from the list."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.students = []
