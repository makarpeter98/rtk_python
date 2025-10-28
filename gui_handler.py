import tkinter as tk
from queue import Queue
from threading import Lock

class GUIHandler:
    def __init__(self, save_queue: Queue, gps_lock: Lock, my_gps_data):
        self.save_queue = save_queue
        self.gps_lock = gps_lock
        self.my_gps_data = my_gps_data

        self.comment_text = ""
        self.stop_threads = False

        self.root = tk.Tk()
        self.root.title("GPS Mentés")
        self.root.geometry("400x200")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self._build_widgets()

    def _build_widgets(self):
        tk.Label(self.root, text="Komment:").pack()
        self.comment_entry = tk.Entry(self.root, width=50)
        self.comment_entry.pack(pady=5)

        self.save_button = tk.Button(self.root, text="GPS Mentése", command=self.save_button_clicked)
        self.save_button.pack(pady=10)

        self.status_label = tk.Label(self.root, text="Várakozás...", wraplength=380)
        self.status_label.pack()

    def save_button_clicked(self):
        self.comment_text = self.comment_entry.get()
        
        with self.gps_lock:
            self.my_gps_data.comment = self.comment_text
        self.status_label.config( text=f"gui_handler: Mentve: lat={self.my_gps_data.latitude}, lon={self.my_gps_data.longitude}\nComment: {self.my_gps_data.comment}" )
        print(f"comment={self.my_gps_data.comment}")
        self.save_queue.put(True)

    def on_close(self):
        print("Ablak bezárva, lezárás folyamatban...")
        self.root.destroy()

    def run(self):
        self.root.mainloop()
