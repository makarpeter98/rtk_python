# drawing.py
from math import cos, radians

def draw_grid(canvas, w, h, step):
    for x in range(0, w, step):
        canvas.create_line(x, 0, x, h, fill="#e0e0e0")
    for y in range(0, h, step):
        canvas.create_line(0, y, w, y, fill="#e0e0e0")


def draw_points(view, pts, meters_per_pixel):
    canvas = view.canvas
    cx = canvas.winfo_width() / 2
    cy = canvas.winfo_height() / 2

    pixel_points = []

    # Nem mentett pontok (piros)
    if view.show_unsaved.get():
        for index, (lat, lon, stored) in enumerate(pts):
            if stored or index == len(pts) - 1:
                continue
            x, y = _gps_to_pixel(view, lat, lon, meters_per_pixel, cx, cy)
            pixel_points.append((x, y))
            canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")

    # Mentett pontok (zöld)
    if view.show_saved.get():
        for index, (lat, lon, stored) in enumerate(pts):
            if not stored or index == len(pts) - 1:
                continue
            x, y = _gps_to_pixel(view, lat, lon, meters_per_pixel, cx, cy)
            pixel_points.append((x, y))
            canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill="green")

    # Aktuális pont (kék)
    if view.show_current.get() and pts:
        lat, lon, stored = pts[-1]
        x, y = _gps_to_pixel(view, lat, lon, meters_per_pixel, cx, cy)
        pixel_points.append((x, y))
        canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="blue")

    # Trajektória
    if view.show_traj.get() and len(pixel_points) > 1:
        for i in range(len(pixel_points) - 1):
            x1, y1 = pixel_points[i]
            x2, y2 = pixel_points[i + 1]
            canvas.create_line(x1, y1, x2, y2, fill="red", width=2)


def _gps_to_pixel(view, lat, lon, meters_per_pixel, cx, cy):
    dx_m = (lon - view.center_lon) * 111000 * cos(radians(view.center_lat))
    dy_m = (lat - view.center_lat) * 111000
    x = cx + dx_m / meters_per_pixel
    y = cy - dy_m / meters_per_pixel
    return x, y
