import tkinter as tk
from queue import Queue
from threading import Lock

class DatabaseView:
    """Placeholder – később kerül kitöltésre."""
    def __init__(self, parent, language):
        self.frame = tk.Frame(parent)
        tk.Label(self.frame, text="Adatbázis nézet – fejlesztés alatt").pack()

    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
