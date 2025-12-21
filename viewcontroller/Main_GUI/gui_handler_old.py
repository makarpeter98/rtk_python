import tkinter as tk
from queue import Queue
from threading import Lock

class GUIHandler:
    def __init__(self, save_queue: Queue, gps_lock: Lock, my_gps_data):
        self.save_queue = save_queue
        self.gps_lock = gps_lock
        self.my_gps_data = my_gps_data
        self.comment_text = ""

        self.root = tk.Tk()
        self.root.title("GPS Mentés")
        self.root.geometry("500x350")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.labels = {}  # a GPS mezők labeljei
        self._build_widgets()

        # GUI frissítés indítása
        self.update_labels()

    def _build_widgets(self):
        tk.Label(self.root, text="Komment:").pack()
        self.comment_entry = tk.Entry(self.root, width=60)
        self.comment_entry.pack(pady=5)

        self.save_button = tk.Button(self.root, text="GPS Mentése", command=self.save_button_clicked)
        self.save_button.pack(pady=10)

        # Status és GPS mezők
        gps_fields = [
            "Latitude", "Longitude", "Latitude error", "Longitude error",
            "Speed", "Mode", "Comment", "Time"
        ]
        for field in gps_fields:
            frame = tk.Frame(self.root)
            frame.pack(anchor="w", padx=10)
            tk.Label(frame, text=f"{field}: ", width=15, anchor="w").pack(side="left")
            lbl = tk.Label(frame, text="", width=30, anchor="w")
            lbl.pack(side="left")
            self.labels[field] = lbl

        self.status_label = tk.Label(self.root, text="Várakozás...", wraplength=480)
        self.status_label.pack(pady=10)

    def save_button_clicked(self):
        self.comment_text = self.comment_entry.get()
        
        with self.gps_lock:
            self.my_gps_data.comment = self.comment_text

        self.status_label.config(
            text=f"gui_handler: Mentve: lat={self.my_gps_data.latitude}, lon={self.my_gps_data.longitude}\nComment: {self.my_gps_data.comment}"
        )
        print(f"comment={self.my_gps_data.comment}")
        self.save_queue.put(True)

    def update_labels(self):
        with self.gps_lock:
            # Frissítjük a label-eket a GPS adatokkal
            self.labels["Latitude"].config(text=str(self.my_gps_data.latitude))
            self.labels["Longitude"].config(text=str(self.my_gps_data.longitude))
            self.labels["Latitude error"].config(text=str(self.my_gps_data.latitude_error))
            self.labels["Longitude error"].config(text=str(self.my_gps_data.longitude_error))
            self.labels["Speed"].config(text=str(self.my_gps_data.speed))
            self.labels["Mode"].config(text=str(self.my_gps_data.mode))
            self.labels["Comment"].config(text=str(self.my_gps_data.comment))
            self.labels["Time"].config(text=str(self.my_gps_data.time))

        # 1 másodpercenként frissít
        self.root.after(10, self.update_labels)

    def on_close(self):
        print("Ablak bezárva, lezárás folyamatban...")
        self.root.destroy()

    def run(self):
        self.root.mainloop()
