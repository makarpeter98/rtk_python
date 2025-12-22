# interactions.py
from math import cos, radians

def bind_interactions(view):
    view.canvas.bind("<ButtonPress-1>", lambda e: on_mouse_down(view, e))
    view.canvas.bind("<B1-Motion>", lambda e: on_mouse_drag(view, e))
    view.canvas.bind("<MouseWheel>", lambda e: on_mouse_wheel(view, e))
    view.canvas.bind("<Button-4>", lambda e: on_mouse_wheel_linux(view, e))
    view.canvas.bind("<Button-5>", lambda e: on_mouse_wheel_linux(view, e))


def on_mouse_down(view, event):
    view.drag_start_x = event.x
    view.drag_start_y = event.y


def on_mouse_drag(view, event):
    if view.center_lat is None:
        return

    dx = event.x - view.drag_start_x
    dy = event.y - view.drag_start_y

    grid_m = view.get_grid_distance_m()
    meters_per_pixel = grid_m / 50

    dx_m = dx * meters_per_pixel
    dy_m = dy * meters_per_pixel

    view.center_lon -= dx_m / (111000 * cos(radians(view.center_lat)))
    view.center_lat += dy_m / 111000

    view.drag_start_x = event.x
    view.drag_start_y = event.y


def on_mouse_wheel(view, event):
    if event.delta < 0:
        view.zoom_slider.set(min(100, view.zoom_slider.get() + 3))
    else:
        view.zoom_slider.set(max(0, view.zoom_slider.get() - 3))


def on_mouse_wheel_linux(view, event):
    if event.num == 5:
        view.zoom_slider.set(min(100, view.zoom_slider.get() + 3))
    elif event.num == 4:
        view.zoom_slider.set(max(0, view.zoom_slider.get() - 3))
