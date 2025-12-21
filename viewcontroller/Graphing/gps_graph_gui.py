import tkinter as tk
from threading import Lock
from math import cos, radians

class GPSGraphGUI:
    def __init__(self, gps_lock: Lock, gps_data):
        self.gps_lock = gps_lock
        self.gps_data = gps_data
        self.points = []  # lista a pontok tárolására (x, y)
        self.origin = None  # az első mérés legyen a (0,0)
        self.meters_per_pixel = 0.1  # 1 m → 10 pixel, sokkal jobban látszik a mozgás

        # Tkinter ablak
        self.root = tk.Tk()
        self.root.title("GPS Pontok Grafikonja")
        self.root.geometry("600x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.canvas = tk.Canvas(self.root, bg="white", width=580, height=580)
        self.canvas.pack(padx=10, pady=10)

        # Rácsok
        self.draw_grid()

        # Indítjuk a frissítést
        self.update_canvas()

    def draw_grid(self):
        """Vízszintes és függőleges rácsok rajzolása 1 méteres távolságokkal (pixel = 1 m)."""
        spacing = 50  # 50 pixel = 50 m, tetszőlegesen állítható
        for i in range(0, 580, spacing):
            # függőleges vonalak
            self.canvas.create_line(i, 0, i, 580, fill="#ddd")
            # vízszintes vonalak
            self.canvas.create_line(0, i, 580, i, fill="#ddd")

    def update_canvas(self):
        with self.gps_lock:
            lat = self.gps_data.latitude
            lon = self.gps_data.longitude

        if lat is not None and lon is not None:
            # Beállítjuk az origin-t az első méréshez
            if self.origin is None:
                self.origin = (lat, lon)
                self.origin_lat_rad = radians(lat)

            # Fokok -> méter
            delta_lat_m = (lat - self.origin[0]) * 111_000
            delta_lon_m = (lon - self.origin[1]) * 111_000 * cos(self.origin_lat_rad)

            # Canvas koordináták
            x = 290 + delta_lon_m / self.meters_per_pixel
            y = 290 - delta_lat_m / self.meters_per_pixel

            self.points.append((x, y))

            # Új pont rajzolása
            r = 4
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="red")

        # Frissítés 1 Hz (1000 ms)
        self.root.after(10, self.update_canvas)

    def on_close(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()
