"""Clase base para todas las pestañas de la UI."""
import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod

class BaseTab(ABC):
    """
    Clase base abstracta para pestañas.
    
    Cada pestaña hereda de esta y debe implementar _build_ui().
    """
    
    def __init__(self, parent, app):
        """
        Args:
            parent: Widget padre (Notebook generalmente)
            app: Referencia a la aplicación principal (InscripcionApp)
        """
        self.parent = parent
        self.app = app
        
        # Frame principal de la pestaña
        self.frame = ttk.Frame(parent, padding=10)
        
        # Construir UI específica de la pestaña
        self._build_ui()
    
    @abstractmethod
    def _build_ui(self):
        """
        Construye la interfaz de la pestaña.
        Debe ser implementado por cada subclase.
        """
        pass
    
    def show_error(self, title, message):
        """Muestra messagebox de error."""
        try:
            messagebox.showerror(title, message)
        except Exception:
            pass
    
    def show_warning(self, title, message):
        """Muestra messagebox de advertencia."""
        try:
            messagebox.showwarning(title, message)
        except Exception:
            pass
    
    def show_info(self, title, message):
        """Muestra messagebox de información."""
        try:
            messagebox.showinfo(title, message)
        except Exception:
            pass
    
    def ask_yes_no(self, title, message):
        """
        Muestra messagebox de confirmación.
        Returns: bool
        """
        try:
            return messagebox.askyesno(title, message)
        except Exception:
            return False
    
    def refresh(self):
        """
        Hook para refrescar contenido de la pestaña.
        Subclases pueden sobrescribir si necesitan refresh.
        """
        pass