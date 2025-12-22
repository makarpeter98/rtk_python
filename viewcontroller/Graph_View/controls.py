# controls.py
import tkinter as tk

def build_controls(view, frame):

    # Pontszám csúszka
    tk.Label(frame, text=view.lang.t("graph_view", "points_number_to_show")).pack()
    view.slider = tk.Scale(frame, from_=1, to=200, orient="horizontal", length=150)
    view.slider.set(50)
    view.slider.pack(pady=10)

    # Zoom csúszka
    tk.Label(frame, text=view.lang.t("graph_view", "Zoom_1cm_to_10km")).pack()
    view.zoom_slider = tk.Scale(frame, from_=0, to=100, orient="horizontal", length=150)
    view.zoom_slider.set(50)
    view.zoom_slider.pack(pady=10)

    # Checkboxok
    view.show_traj = tk.BooleanVar(value=True)
    view.show_saved = tk.BooleanVar(value=True)
    view.show_unsaved = tk.BooleanVar(value=True)
    view.show_current = tk.BooleanVar(value=True)

    tk.Checkbutton(frame, text=view.lang.t("graph_view", "show_trajectory"), variable=view.show_traj).pack(fill="x", pady=5)
    tk.Checkbutton(frame, text=view.lang.t("graph_view", "show_saved_points"), variable=view.show_saved).pack(fill="x", pady=5)
    tk.Checkbutton(frame, text=view.lang.t("graph_view", "show_unsaved_points"), variable=view.show_unsaved).pack(fill="x", pady=5)
    tk.Checkbutton(frame, text=view.lang.t("graph_view", "show_current_point"), variable=view.show_current).pack(fill="x", pady=5)

    # Gombok
    tk.Button(frame, text=view.lang.t("graph_view", "save_button"), command=view.save_button_clicked).pack(fill="x", pady=5)
    tk.Button(frame, text=view.lang.t("graph_view", "center_button"), command=view.center_on_last).pack(fill="x", pady=5)
    tk.Button(frame, text=view.lang.t("graph_view", "clear_graph"), command=view.clear_graph).pack(fill="x", pady=5)

    # Rácsköz kiírása
    tk.Label(frame, text=view.lang.t("graph_view", "frame_distance")).pack()
    view.grid_label = tk.Label(frame, text="---")
    view.grid_label.pack(pady=5)
