import tkinter as tk
from queue import Queue
from threading import Lock

class MeasurementView:
    def __init__(self, parent, gps_lock, my_gps_data, lang):
        self.parent = parent
        self.gps_lock = gps_lock
        self.my_gps_data = my_gps_data
        self.lang = lang

        self.labels = {}
        self.comment_text = ""

        self.frame = tk.Frame(self.parent)
        self._build_widgets()

    def _build_widgets(self):
        tk.Label(self.frame, text=self.lang.t("measurement_view", "comment_label")).pack()

        self.comment_entry = tk.Entry(self.frame, width=60)
        self.comment_entry.pack(pady=5)

        self.save_button = tk.Button(
            self.frame,
            text=self.lang.t("measurement_view", "save_button"),
            command=self.save_button_clicked
        )
        self.save_button.pack(pady=10)

        # GPS mezők magyar nevei a JSON-ból
        fields = self.lang.t("measurement_view", "fields")

        for key, label_hu in fields.items():
            row = tk.Frame(self.frame)
            row.pack(anchor="w", padx=10)
            tk.Label(row, text=f"{label_hu}: ", width=15, anchor="w").pack(side="left")
            lbl = tk.Label(row, text="", width=30, anchor="w")
            lbl.pack(side="left")
            self.labels[key] = lbl

        self.status_label = tk.Label(
            self.frame,
            text=self.lang.t("measurement_view", "status_wait"),
            wraplength=480
        )
        self.status_label.pack(pady=10)

    def save_button_clicked(self):
        self.comment_text = self.comment_entry.get()
        #print("Mentés elkezdve!")
        with self.gps_lock:
            self.my_gps_data.comment = self.comment_text
            self.my_gps_data.store_gps_data = True

        units = self.lang.t("measurement_view", "units")
        self.status_label.config(
            text=f"{self.lang.t('measurement_view', 'status_saved')}\n"
                 f"{self.lang.t('measurement_view', 'fields', 'Latitude')}: "
                 f"{self.my_gps_data.latitude} {units['Latitude']}, "
                 f"{self.lang.t('measurement_view', 'fields', 'Longitude')}: "
                 f"{self.my_gps_data.longitude} {units['Longitude']}\n"
                 f"{self.lang.t('measurement_view', 'fields', 'Comment')}: "
                 f"{self.my_gps_data.comment}"
        )
        
        #self.my_gps_data.store_gps_data = True
        
        #self.save_queue.put(True)

    def update(self):
        with self.gps_lock:
            units = self.lang.t("measurement_view", "units")

            self.labels["Latitude"].config(
                text=f"{self.my_gps_data.latitude} {units['Latitude']}"
            )
            self.labels["Longitude"].config(
                text=f"{self.my_gps_data.longitude} {units['Longitude']}"
            )
            self.labels["Latitude error"].config(
                text=f"{self.my_gps_data.latitude_error} {units['Latitude error']}"
            )
            self.labels["Longitude error"].config(
                text=f"{self.my_gps_data.longitude_error} {units['Longitude error']}"
            )
            self.labels["Speed"].config(
                text=f"{self.my_gps_data.speed} {units['Speed']}"
            )
            self.labels["Mode"].config(
                text=f"{self.my_gps_data.mode} {units['Mode']}"
            )
            self.labels["Comment"].config(
                text=f"{self.my_gps_data.comment} {units['Comment']}"
            )
            self.labels["Time"].config(
                text=f"{self.my_gps_data.time} {units['Time']}"
            )
            """self.labels["Save"].config(
                text=f"{self.my_gps_data.store_gps_data} {units['Save']}"
            )"""

    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
