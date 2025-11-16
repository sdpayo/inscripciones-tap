"""Punto de entrada de la aplicación."""
import tkinter as tk
from ui.app import InscripcionApp

def main():
    root = tk.Tk()
    app = InscripcionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()