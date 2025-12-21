import tkinter as tk
from math import cos, radians

class GraphView:
    """GPS pontok kirajzolása szélesség/hosszúság alapján."""
    def __init__(self, parent, lang, my_gps_data):
        self.lang = lang
        self.my_gps_data = my_gps_data
        self.last_lat = None
        self.last_lon = None

        # GPS pontok (lat, lon)
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
        tk.Label(control_frame, text="Megjelenített pontok száma").pack()
        self.slider = tk.Scale(control_frame, from_=1, to=200, orient="horizontal", length=150)
        self.slider.set(50)
        self.slider.pack(pady=10)

        # Zoom csúszka
        tk.Label(control_frame, text="Zoom (10 cm → 10 km)").pack()
        self.zoom_slider = tk.Scale(control_frame, from_=0, to=100, orient="horizontal", length=150)
        self.zoom_slider.set(50)
        self.zoom_slider.pack(pady=10)

        # Trajektória kapcsoló
        self.show_traj = tk.BooleanVar(value=True)
        tk.Checkbutton(
            control_frame,
            text="Trajektória mutatása",
            variable=self.show_traj,
            onvalue=True,
            offvalue=False
        ).pack(fill="x", pady=5)

        # Gombok
        tk.Button(control_frame, text="JPG Export").pack(fill="x", pady=5)
        tk.Button(control_frame, text="Középre ugrás", command=self.center_on_last).pack(fill="x", pady=5)
        
        # Rácsköz kiírása
        tk.Label(control_frame, text="Rácsköz:").pack()
        self.grid_label = tk.Label(control_frame, text="---")
        self.grid_label.pack(pady=5)

    # ---------------------------------------------------------
    #   Logaritmikus zoom → rácsköz méterben
    # ---------------------------------------------------------
    def get_grid_distance_m(self):
        slider_value = self.zoom_slider.get()  # 0–100

        min_m = 0.01      # 1 cm
        max_m = 10000    # 10 km

        ratio = slider_value / 100
        return min_m * ((max_m / min_m) ** ratio)

    # ---------------------------------------------------------
    #   GPS pontok frissítése
    # ---------------------------------------------------------
    def update(self):
        lat = self.my_gps_data.latitude
        lon = self.my_gps_data.longitude

        if not (lat == 0.0 and lon == 0.0):
            if (lat, lon) != (self.last_lat, self.last_lon):
                self.points.append((lat, lon))
                self.last_lat = lat
                self.last_lon = lon

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
        
        # Rácsköz méterben
        grid_m = self.get_grid_distance_m()
        pixels_per_grid = 50
        meters_per_pixel = grid_m / pixels_per_grid

        # Rácsköz kiírása
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

        # Rácsköz méterben
        grid_m = self.get_grid_distance_m()
        pixels_per_grid = 50
        meters_per_pixel = grid_m / pixels_per_grid

        # Rács
        self._draw_grid(w, h, pixels_per_grid)

        cx = w / 2
        cy = h / 2

        # Pontok kirajzolása
        pixel_points = []  # tároljuk a pixel koordinátákat a trajektóriához

        for index, (lat, lon) in enumerate(pts):
            dx_m = (lon - self.center_lon) * 111000 * cos(radians(self.center_lat))
            dy_m = (lat - self.center_lat) * 111000

            x = cx + dx_m / meters_per_pixel
            y = cy - dy_m / meters_per_pixel

            pixel_points.append((x, y))

            # ✅ Az utolsó pont legyen kék
            if index == len(pts) - 1:
                color = "blue"
            else:
                color = "red"

            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color)


        # Trajektória kirajzolása
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
        """Az utolsó GPS pontot a grafikon közepére helyezi."""
        if not self.points:
            return

        # Utolsó pont
        lat, lon = self.points[-1]

        # Középpont átállítása
        self.center_lat = lat
        self.center_lon = lon

        # Újrarajzolás
        max_points = self.slider.get()
        pts = self.points[-max_points:]
        self._draw_points(pts)
    
    def format_distance(self, meters):
        """Rácsköz távolság formázása cm / m / km egységben."""
        if meters < 1:
            # 1 m alatt → cm
            return f"{meters*100:.1f} cm"
        elif meters < 1000:
            # 1 m – 1000 m → m
            return f"{meters:.2f} m"
        else:
            # 1 km felett → km
            return f"{meters/1000:.3f} km"


    # ---------------------------------------------------------
    #   View kezelés
    # ---------------------------------------------------------
    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
