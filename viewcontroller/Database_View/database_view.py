import tkinter as tk
from tkinter import ttk
from model.DB_handler.database_handler import DataBaseHandler


def fmt(value, fmt_str, suffix="", fallback="—"):
    try:
        return f"{format(float(value), fmt_str)}{suffix}"
    except (TypeError, ValueError):
        return fallback


class DatabaseView:
    def __init__(self, parent, language, my_gps_data_list):
        self.lang = language
        self.my_gps_data_list = my_gps_data_list
        self.db = DataBaseHandler()

        self.frame = tk.Frame(parent)

        # --- Checkboxes ---
        self.show_unsaved_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self.frame,
            text="Nem tárolt pontok mutatása",
            variable=self.show_unsaved_var,
            command=self.refresh_table
        ).pack(anchor="w")

        self.enable_color_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self.frame,
            text="Színezés engedélyezése",
            variable=self.enable_color_var,
            command=self.refresh_table
        ).pack(anchor="w")

        tk.Button(
            self.frame,
            text="Kijelöltek törlése",
            command=self.delete_selected_rows
        ).pack(anchor="w", pady=5)

        # --- Table ---
        table_frame = tk.Frame(self.frame)
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            table_frame,
            columns=(
                "time", "latitude", "longitude", "speed",
                "latitude_error", "longitude_error",
                "mode", "comment", "selected"
            ),
            show="headings"
        )

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        headers = {
            "time": "Idő",
            "latitude": "Szélesség",
            "longitude": "Hosszúság",
            "speed": "Sebesség",
            "latitude_error": "Szél. hiba",
            "longitude_error": "Hossz. hiba",
            "mode": "Mód",
            "comment": "Megjegyzés",
            "selected": "☐"
        }

        for col, text in headers.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.on_header_click(c))
            self.tree.column(col, width=120, anchor="center")

        self.tree.column("selected", width=40)

        self.header_select_all = False
        self.tree.bind("<Button-1>", self.on_row_click)

        self.refresh_table()

    # ---------------------------------------------------------
    #   Header click
    # ---------------------------------------------------------
    def on_header_click(self, col):
        if col != "selected":
            self.sort_by_column(col)
            return

        self.header_select_all = not self.header_select_all
        self.tree.heading("selected", text="☑" if self.header_select_all else "☐")

        for row in self.tree.get_children():
            self.tree.set(row, "selected", "✔" if self.header_select_all else "")

    # ---------------------------------------------------------
    #   Checkbox click
    # ---------------------------------------------------------
    def on_row_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        col = self.tree.identify_column(event.x)
        if col != f"#{len(self.tree['columns'])}":
            return

        row = self.tree.identify_row(event.y)
        if not row:
            return

        current = self.tree.set(row, "selected")
        self.tree.set(row, "selected", "" if current == "✔" else "✔")

    # ---------------------------------------------------------
    #   Refresh table
    # ---------------------------------------------------------
    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())

        db_list = self.db.get_all_gps_data()
        unsaved_list = self.my_gps_data_list

        db_keys = {(g.time, g.latitude, g.longitude) for g in db_list}
        unsaved_keys = {(g.time, g.latitude, g.longitude) for g in unsaved_list}

        if self.show_unsaved_var.get():
            full_list = db_list + [
                g for g in unsaved_list
                if (g.time, g.latitude, g.longitude) not in db_keys
            ]
        else:
            full_list = db_list

        for gps in full_list:
            key = (gps.time, gps.latitude, gps.longitude)

            if self.enable_color_var.get():
                if key in db_keys and key in unsaved_keys:
                    tag = "both"
                elif key in db_keys:
                    tag = "db_only"
                else:
                    tag = "unsaved"
            else:
                tag = ""

            self.tree.insert(
                "",
                "end",
                values=(
                    gps.time,
                    fmt(gps.latitude, ".7f", " °"),
                    fmt(gps.longitude, ".7f", " °"),
                    fmt(gps.speed, ".2f", " km/h"),
                    fmt(gps.latitude_error, ".2f", " m"),
                    fmt(gps.longitude_error, ".2f", " m"),
                    gps.mode,
                    gps.comment,
                    ""
                ),
                tags=(tag,)
            )

        self.tree.tag_configure("db_only", background="#a8c5ff")
        self.tree.tag_configure("unsaved", background="#fff3a3")
        self.tree.tag_configure("both", background="#c8ffb0")

    # ---------------------------------------------------------
    #   Delete selected
    # ---------------------------------------------------------
    def delete_selected_rows(self):
        for row in self.tree.get_children():
            if self.tree.set(row, "selected") != "✔":
                continue

            lat_str = self.tree.set(row, "latitude").replace("°", "").strip()
            lon_str = self.tree.set(row, "longitude").replace("°", "").strip()

            try:
                lat = float(lat_str)
                lon = float(lon_str)
            except ValueError:
                continue

            self.db.delete_gps_data_from_db(lat, lon)

        self.refresh_table()

    # ---------------------------------------------------------
    #   Sorting
    # ---------------------------------------------------------
    def sort_by_column(self, col):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            data.sort(key=lambda t: float(t[0].split()[0]))
        except ValueError:
            data.sort(key=lambda t: t[0])

        for index, (_, k) in enumerate(data):
            self.tree.move(k, "", index)

    # ---------------------------------------------------------
    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
