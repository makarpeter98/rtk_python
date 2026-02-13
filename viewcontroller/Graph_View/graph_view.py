# graph_view.py
import tkinter as tk
from .drawing import draw_grid, draw_points
from .interactions import bind_interactions
from .controls import build_controls
from .state import get_grid_distance, center_on_last
import tkinter as tk

class GraphView:
    def __init__(self, parent, lang, my_gps_data_list, my_gps_data, clear_callback):
        self.lang = lang
        self.my_gps_data_list = my_gps_data_list
        self.my_gps_data = my_gps_data
        self.clear_callback = clear_callback

        self.points = []
        self.center_lat = None
        self.center_lon = None
                
        self.always_center = tk.BooleanVar(value=False)

        self.frame = tk.Frame(parent)

        self.canvas = tk.Canvas(self.frame, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        control_frame = tk.Frame(self.frame)
        control_frame.pack(side="right", fill="y", padx=10, pady=10)

        build_controls(self, control_frame)
        bind_interactions(self)

    def get_grid_distance_m(self):
        return get_grid_distance(self)

    def update(self):
        for gps in self.my_gps_data_list:
            if isinstance(gps.latitude, float) and isinstance(gps.longitude, float):
                if not (gps.latitude == 0.0 and gps.longitude == 0.0):
                    self.points.append((gps.latitude, gps.longitude, gps.store_gps_data))

                    # Első pontnál alap közép
                    if self.center_lat is None:
                        self.center_lat = gps.latitude
                        self.center_lon = gps.longitude

        if not self.points:
            return

        # Always center logika
        if hasattr(self, "always_center") and self.always_center.get():
            lat, lon, _ = self.points[-1]
            self.center_lat = lat
            self.center_lon = lon

        pts = self.points[-self.slider.get():]
        self._draw(pts)


    def _draw(self, pts):
        self.canvas.delete("all")

        if not pts or self.center_lat is None:
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        draw_grid(self.canvas, w, h, 50)

        grid_m = self.get_grid_distance_m()
        meters_per_pixel = grid_m / 50

        self.grid_label.config(text=self.format_distance(grid_m))
        draw_points(self, pts, meters_per_pixel)

    def clear_graph(self):
        self.clear_callback()
        self.points.clear()
        self.center_lat = None
        self.center_lon = None
        self.canvas.delete("all")
        self.grid_label.config(text="---")

    def center_on_last(self):
        center_on_last(self)

    def save_button_clicked(self):
        self.my_gps_data.store_gps_data = True
        self.my_gps_data.comment = "AUTO_GRAPH_COMMENT"

    def format_distance(self, meters):
        if meters < 1:
            return f"{meters * 100:.1f} cm"
        elif meters < 1000:
            return f"{meters:.2f} m"
        else:
            return f"{meters / 1000:.3f} km"

    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
