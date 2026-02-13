import tkinter as tk


class MeasurementView:
    def __init__(self, parent, gps_lock, my_gps_data, lang):
        self.parent = parent
        self.gps_lock = gps_lock
        self.my_gps_data = my_gps_data
        self.lang = lang

        self.labels = {}
        self.field_name_labels = {}

        self.frame = tk.Frame(self.parent)

        # nyelvválasztó (angol az alapértelmezett)
        self.language_var = tk.StringVar(value="English")

        self._build_widgets()

    def _build_widgets(self):
        # ===== Language selector =====
        lang_frame = tk.Frame(self.frame)
        lang_frame.pack(anchor="e", padx=10, pady=5)

        tk.Label(lang_frame, text="Language:").pack(side="left")

        tk.OptionMenu(
            lang_frame,
            self.language_var,
            "English",
            "Magyar",
            command=self.change_language
        ).pack(side="left")

        # ===== Comment =====
        self.comment_label = tk.Label(
            self.frame,
            text=self.lang.t("measurement_view", "comment_label")
        )
        self.comment_label.pack()

        self.comment_entry = tk.Entry(self.frame, width=60)
        self.comment_entry.pack(pady=5)

        # ===== Save button =====
        self.save_button = tk.Button(
            self.frame,
            text=self.lang.t("measurement_view", "save_button"),
            command=self.save_button_clicked
        )
        self.save_button.pack(pady=10)

        # ===== GPS fields =====
        fields = self.lang.t("measurement_view", "fields")

        for key, label_text in fields.items():
            row = tk.Frame(self.frame)
            row.pack(anchor="w", padx=10)

            name_label = tk.Label(row, text=f"{label_text}: ", width=18, anchor="w")
            name_label.pack(side="left")

            value_label = tk.Label(row, text="", width=30, anchor="w")
            value_label.pack(side="left")

            self.field_name_labels[key] = name_label
            self.labels[key] = value_label

        # ===== Status =====
        self.status_label = tk.Label(
            self.frame,
            text=self.lang.t("measurement_view", "status_wait"),
            wraplength=480
        )
        self.status_label.pack(pady=10)

    # ===============================
    # Language switching
    # ===============================
    def change_language(self, selection):
        if selection == "English":
            self.lang.load_language("en")
        elif selection == "Magyar":
            self.lang.load_language("hu")

        self.refresh_texts()

    def refresh_texts(self):
        self.comment_label.config(
            text=self.lang.t("measurement_view", "comment_label")
        )

        self.save_button.config(
            text=self.lang.t("measurement_view", "save_button")
        )

        self.status_label.config(
            text=self.lang.t("measurement_view", "status_wait")
        )

        fields = self.lang.t("measurement_view", "fields")
        for key, label_text in fields.items():
            self.field_name_labels[key].config(text=f"{label_text}: ")

    # ===============================
    # Button action
    # ===============================
    def save_button_clicked(self):
        comment = self.comment_entry.get()

        with self.gps_lock:
            self.my_gps_data.comment = comment
            self.my_gps_data.store_gps_data = True

            lat = self.my_gps_data.latitude
            lon = self.my_gps_data.longitude

        units = self.lang.t("measurement_view", "units")

        self.status_label.config(
            text=f"{self.lang.t('measurement_view', 'status_saved')}\n"
                 f"{self.lang.t('measurement_view', 'fields', 'Latitude')}: "
                 f"{lat} {units['Latitude']}, "
                 f"{self.lang.t('measurement_view', 'fields', 'Longitude')}: "
                 f"{lon} {units['Longitude']}\n"
                 f"{self.lang.t('measurement_view', 'fields', 'Comment')}: {comment}"
        )

    # ===============================
    # Update GPS values
    # ===============================
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
                text=f"{self.my_gps_data.mode}"
            )
            self.labels["Comment"].config(
                text=f"{self.my_gps_data.comment}"
            )
            self.labels["Time"].config(
                text=f"{self.my_gps_data.time}"
            )

    # ===============================
    # Visibility
    # ===============================
    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
