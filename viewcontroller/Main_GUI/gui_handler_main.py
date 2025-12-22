import tkinter as tk
from queue import Queue
from threading import Lock

from viewcontroller.Measure_View.measurement_view import MeasurementView
from viewcontroller.Graph_View.graph_view import GraphView
from viewcontroller.Database_View.database_view import DatabaseView
from viewcontroller.Main_GUI.language_manager import LanguageManager


class GUIHandler:
    def __init__(self, gps_lock: Lock, my_gps_data, my_gps_data_list, clear_callback):

        # --- Nyelvi csomag betöltése ---
        self.lang = LanguageManager("viewcontroller/Main_GUI/lang_hu.json")

        self.gps_lock = gps_lock
        self.my_gps_data = my_gps_data
        self.my_gps_data_list = my_gps_data_list
        self.clear_callback = clear_callback   # <-- FONTOS

        self.root = tk.Tk()
        self.root.title("GPS GUI")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Menü gombok
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(fill="x")

        tk.Button(
            self.menu_frame,
            text=self.lang.t("menu", "measurement"),
            width=15,
            command=lambda: self.switch_view("measurement")
        ).pack(side="left")

        tk.Button(
            self.menu_frame,
            text=self.lang.t("menu", "graph"),
            width=15,
            command=lambda: self.switch_view("graph")
        ).pack(side="left")

        tk.Button(
            self.menu_frame,
            text=self.lang.t("menu", "database"),
            width=15,
            command=lambda: self.switch_view("db")
        ).pack(side="left")

        # Tartalom helye
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True)

        # Nézetek
        self.views = {
            "measurement": MeasurementView(self.content_frame, gps_lock, my_gps_data, self.lang),
            "graph": GraphView(self.content_frame, self.lang, my_gps_data_list, my_gps_data, self.clear_callback),
            "db": DatabaseView(self.content_frame, self.lang, my_gps_data_list)
        }

        self.current_view = None
        self.switch_view("measurement")  # alapértelmezett

        self.update_loop()

    def switch_view(self, name):
        if self.current_view:
            self.current_view.hide()

        self.current_view = self.views[name]
        self.current_view.show()

    def update_loop(self):
        """10 ms-enként frissítjük a nézetet."""
        if hasattr(self.current_view, "update"):
            self.current_view.update()

        self.root.after(10, self.update_loop)

    def on_close(self):
        print("GUI bezárva...")
        self.root.destroy()

    def run(self):
        self.root.mainloop()
