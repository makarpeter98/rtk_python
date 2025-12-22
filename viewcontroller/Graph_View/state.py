# state.py

def get_grid_distance(view):
    slider_value = view.zoom_slider.get()
    min_m = 0.01
    max_m = 10000
    ratio = slider_value / 100
    return min_m * ((max_m / min_m) ** ratio)


def center_on_last(view):
    if not view.points:
        return
    lat, lon, stored = view.points[-1]
    view.center_lat = lat
    view.center_lon = lon
