import tkinter as tk
from math import cos, radians

class GraphView:
    """GPS pontok kirajzolása szélesség/hosszúság alapján."""
    def __init__(self, parent, lang, my_gps_data_list, my_gps_data, clear_callback):
        self.lang = lang
        self.my_gps_data_list = my_gps_data_list
        self.my_gps_data = my_gps_data  # <-- szükséges a mentéshez
        self.clear_callback = clear_callback

        # GPS pontok (lat, lon, stored)
        self.points = []

        # Az első pont lesz a középpont
        self.center_lat = None
        self.center_lon = None

        # Fő frame
        self.frame = tk.Frame(parent)

        # Bal oldal: grafikon
        self.canvas = tk.Canvas(self.frame, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Jobb oldal: vezérlők
        control_frame = tk.Frame(self.frame)
        control_frame.pack(side="right", fill="y", padx=10, pady=10)

        # Csúszka: utolsó N pont
        tk.Label(control_frame, text=self.lang.t("graph_view", "points_number_to_show")).pack()
        self.slider = tk.Scale(control_frame, from_=1, to=200, orient="horizontal", length=150)
        self.slider.set(50)
        self.slider.pack(pady=10)

        # Zoom csúszka
        tk.Label(control_frame, text=self.lang.t("graph_view", "Zoom_1cm_to_10km")).pack()
        self.zoom_slider = tk.Scale(control_frame, from_=0, to=100, orient="horizontal", length=150)
        self.zoom_slider.set(50)
        self.zoom_slider.pack(pady=10)

        # Trajektória kapcsoló
        self.show_traj = tk.BooleanVar(value=True)
        tk.Checkbutton(
            control_frame,
            text=self.lang.t("graph_view", "show_trajectory"),
            variable=self.show_traj
        ).pack(fill="x", pady=5)

        # ÚJ: mentett pontok mutatása
        self.show_saved = tk.BooleanVar(value=True)
        tk.Checkbutton(
            control_frame,
            text=self.lang.t("graph_view", "show_saved_points"),
            variable=self.show_saved
        ).pack(fill="x", pady=5)

        # ÚJ: nem mentett pontok mutatása
        self.show_unsaved = tk.BooleanVar(value=True)
        tk.Checkbutton(
            control_frame,
            text=self.lang.t("graph_view", "show_unsaved_points"),
            variable=self.show_unsaved
        ).pack(fill="x", pady=5)

        # ÚJ: aktuális pont mutatása
        self.show_current = tk.BooleanVar(value=True)
        tk.Checkbutton(
            control_frame,
            text=self.lang.t("graph_view", "show_current_point"),
            variable=self.show_current
        ).pack(fill="x", pady=5)

        # Mentés gomb
        tk.Button(
            control_frame,
            text=self.lang.t("graph_view", "save_button"),
            command=self.save_button_clicked
        ).pack(fill="x", pady=5)

        # Középre igazítás gomb
        tk.Button(
            control_frame,
            text=self.lang.t("graph_view", "center_button"),
            command=self.center_on_last
        ).pack(fill="x", pady=5)
        
        tk.Button(
            control_frame,
            text=self.lang.t("graph_view", "clear_graph"),
            command=self.clear_graph
        ).pack(fill="x", pady=5)


        # Rácsköz kiírása
        tk.Label(control_frame, text=self.lang.t("graph_view", "frame_distance")).pack()
        self.grid_label = tk.Label(control_frame, text="---")
        self.grid_label.pack(pady=5)

        # Egér húzás támogatása
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)

        self.drag_start_x = None
        self.drag_start_y = None

        # Görgős zoom
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)      # Windows / macOS
        self.canvas.bind("<Button-4>", self.on_mouse_wheel_linux)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel_linux)  # Linux scroll down

    # ---------------------------------------------------------
    #   Logaritmikus zoom → rácsköz méterben
    # ---------------------------------------------------------
    def get_grid_distance_m(self):
        slider_value = self.zoom_slider.get()  # 0–100

        min_m = 0.01     # 1 cm
        max_m = 10000    # 10 km

        ratio = slider_value / 100
        return min_m * ((max_m / min_m) ** ratio)

    # ---------------------------------------------------------
    #   GPS pontok frissítése
    # ---------------------------------------------------------
    def update(self):
        
        for my_gps_data in self.my_gps_data_list:
            lat = my_gps_data.latitude
            lon = my_gps_data.longitude

            if isinstance(lat, float) and isinstance(lon, float):
                if not (lat == 0.0 and lon == 0.0):
                    self.points.append((lat, lon, my_gps_data.store_gps_data))

                    if self.center_lat is None:
                        self.center_lat = lat
                        self.center_lon = lon

        max_points = self.slider.get()
        pts = self.points[-max_points:]
        self._draw_points(pts)

    # ---------------------------------------------------------
    #   Pontok kirajzolása
    # ---------------------------------------------------------
    def _draw_points(self, pts):
        grid_m = self.get_grid_distance_m()
        pixels_per_grid = 50
        meters_per_pixel = grid_m / pixels_per_grid

        self.grid_label.config(text=self.format_distance(grid_m))

        if self.center_lat is None or self.center_lon is None:
            return

        self.canvas.delete("all")

        if not pts:
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return

        self._draw_grid(w, h, pixels_per_grid)

        cx = w / 2
        cy = h / 2

        pixel_points = []

        # 1) Piros pontok (nem mentett)
        if self.show_unsaved.get():
            for index, (lat, lon, stored) in enumerate(pts):
                if stored:
                    continue
                if index == len(pts) - 1:
                    continue

                dx_m = (lon - self.center_lon) * 111000 * cos(radians(self.center_lat))
                dy_m = (lat - self.center_lat) * 111000

                x = cx + dx_m / meters_per_pixel
                y = cy - dy_m / meters_per_pixel

                pixel_points.append((x, y))
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")

        # 2) Zöld pontok (mentett)
        if self.show_saved.get():
            for index, (lat, lon, stored) in enumerate(pts):
                if not stored:
                    continue
                if index == len(pts) - 1:
                    continue

                dx_m = (lon - self.center_lon) * 111000 * cos(radians(self.center_lat))
                dy_m = (lat - self.center_lat) * 111000

                x = cx + dx_m / meters_per_pixel
                y = cy - dy_m / meters_per_pixel

                pixel_points.append((x, y))
                self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill="green")

        # 3) Kék pont (aktuális)
        if self.show_current.get():
            lat, lon, stored = pts[-1]
            dx_m = (lon - self.center_lon) * 111000 * cos(radians(self.center_lat))
            dy_m = (lat - self.center_lat) * 111000

            x_last = cx + dx_m / meters_per_pixel
            y_last = cy - dy_m / meters_per_pixel

            pixel_points.append((x_last, y_last))
            self.canvas.create_oval(x_last - 5, y_last - 5, x_last + 5, y_last + 5, fill="blue")

        # Trajektória
        if self.show_traj.get() and len(pixel_points) > 1:
            for i in range(len(pixel_points) - 1):
                x1, y1 = pixel_points[i]
                x2, y2 = pixel_points[i + 1]
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2)

    # ---------------------------------------------------------
    #   Rács kirajzolása
    # ---------------------------------------------------------
    def _draw_grid(self, w, h, step):
        for x in range(0, w, step):
            self.canvas.create_line(x, 0, x, h, fill="#e0e0e0")
        for y in range(0, h, step):
            self.canvas.create_line(0, y, w, y, fill="#e0e0e0")

    def center_on_last(self):
        if not self.points:
            return

        lat, lon, stored = self.points[-1]
        self.center_lat = lat
        self.center_lon = lon

        max_points = self.slider.get()
        pts = self.points[-max_points:]
        self._draw_points(pts)

    def format_distance(self, meters):
        if meters < 1:
            return f"{meters * 100:.1f} cm"
        elif meters < 1000:
            return f"{meters:.2f} m"
        else:
            return f"{meters / 1000:.3f} km"

    # ---------------------------------------------------------
    #   Egér húzás (pan)
    # ---------------------------------------------------------
    def on_mouse_down(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_mouse_drag(self, event):
        if self.center_lat is None or self.center_lon is None:
            return

        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        grid_m = self.get_grid_distance_m()
        pixels_per_grid = 50
        meters_per_pixel = grid_m / pixels_per_grid

        dx_m = dx * meters_per_pixel
        dy_m = dy * meters_per_pixel

        self.center_lon -= dx_m / (111000 * cos(radians(self.center_lat)))
        self.center_lat += dy_m / 111000

        self.drag_start_x = event.x
        self.drag_start_y = event.y

        max_points = self.slider.get()
        pts = self.points[-max_points:]
        self._draw_points(pts)

    # ---------------------------------------------------------
    #   Görgős zoom
    # ---------------------------------------------------------
    def on_mouse_wheel(self, event):
        if event.delta < 0:
            self.zoom_slider.set(min(100, self.zoom_slider.get() + 3))
        else:
            self.zoom_slider.set(max(0, self.zoom_slider.get() - 3))

        max_points = self.slider.get()
        pts = self.points[-max_points:]
        self._draw_points(pts)

    def on_mouse_wheel_linux(self, event):
        if event.num == 5:
            self.zoom_slider.set(min(100, self.zoom_slider.get() + 3))
        elif event.num == 4:
            self.zoom_slider.set(max(0, self.zoom_slider.get() - 3))

        max_points = self.slider.get()
        pts = self.points[-max_points:]
        self._draw_points(pts)
    
    # ---------------------------------------------------------
    #   Grafikon ürítése gomb
    # ---------------------------------------------------------
    def clear_graph(self):
        print("GraphView → clear_graph()")
        self.clear_callback()   # <-- valódi adat törlése
        self.points.clear()     # saját cache törlése
        self.center_lat = None
        self.center_lon = None
        self.canvas.delete("all")
        self.grid_label.config(text="---")

    
    # ---------------------------------------------------------
    #   Mentés gomb
    # ---------------------------------------------------------
    def save_button_clicked(self):
        if self.my_gps_data is None:
            return

        self.my_gps_data.store_gps_data = True

    # ---------------------------------------------------------
    #   View kezelés
    # ---------------------------------------------------------
    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
