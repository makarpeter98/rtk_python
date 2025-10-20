import threading
import queue
import time
import tkinter as tk
import argparse

from gps_handler import GPSHandler
from gps_data import GPSData
from database_handler import DataBaseHandler

# --- Megosztott objektumok
my_gps_data = GPSData()
gps_lock = threading.Lock()
save_queue = queue.Queue()
stop_threads = False  # a thread-ek leállításához
my_gps_handler = None  # globális GPSHandler objektum
comment_text = ""  # a GUI-ból globális komment

# --- GPS szál ---
def gps_thread():
    global my_gps_data, stop_threads, my_gps_handler
    my_gps_handler = GPSHandler()
    my_gps_handler.connect_to_gps()
    print("gps_thread elindult")
    while not stop_threads:
        with gps_lock:
            my_gps_handler.get_gps_data(my_gps_data)
            print(f"lat={my_gps_data.latitude} lat_err={my_gps_data.latitude_error} "
                  f"lon={my_gps_data.longitude} lon_err={my_gps_data.longitude_error}"
                  f"mode={my_gps_data.mode}")
        time.sleep(0.5)

# --- DB szál ---
def db_thread():
    db_handler = DataBaseHandler()
    global my_gps_data, stop_threads, comment_text
    while not stop_threads:
        try:
            save_queue.get(timeout=0.5)
        except queue.Empty:
            continue
        with gps_lock:
            try:
                if len(comment_text) > 0:
                    my_gps_data.comment = comment_text   
                else:
                    my_gps_data.comment = None
                
                db_handler.save_gps_data(my_gps_data)
                    
                print(f"Mentve: lat={my_gps_data.latitude}, lon={my_gps_data.longitude}, comment={comment_text}")
            except Exception as e:
                print(f"Hiba DB: {e}")
        save_queue.task_done()

# --- GUI szál ---
def gui_thread():
    global stop_threads, comment_text

    def save_button_clicked():
        global comment_text
        comment_text = comment_entry.get()
        save_queue.put(True)
        with gps_lock:
            my_gps_data.comment = comment_text
            status_label.config(
                text=f"Mentve: lat={my_gps_data.latitude:.6f}, lon={my_gps_data.longitude:.6f}\nComment: {comment_text}"
            )
        print(f"comment={comment_text}")

    def on_close():
        global stop_threads, my_gps_handler
        print("Ablak bezárva, lezárás folyamatban...")
        stop_threads = True
        if my_gps_handler is not None:
            my_gps_handler.close_gps_connection()
        root.destroy()

    root = tk.Tk()
    root.title("GPS Mentés")
    root.geometry("400x200")
    root.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(root, text="Komment:").pack()
    comment_entry = tk.Entry(root, width=50)
    comment_entry.pack(pady=5)

    btn = tk.Button(root, text="GPS Mentése", command=save_button_clicked)
    btn.pack(pady=10)

    global status_label
    status_label = tk.Label(root, text="Várakozás...", wraplength=380)
    status_label.pack()

    root.mainloop()

# --- Fő program ---
def main():
    parser = argparse.ArgumentParser(description="RTK GUI + GPS")
    parser.add_argument("-i", "--init", type=str, help="GPS inicializálása", required=True)
    parser.add_argument("-oi", "--only_init", type=str, help="Csak a GPS inicializálása majd kilépés")
    args = parser.parse_args()

    if args.init == "True":
        GPSHandler().initialize_gps()

    if args.only_init == "True":
        print("Csak inicializálás, kilépés...")
        return

    t_gps = threading.Thread(target=gps_thread, daemon=True)
    t_db = threading.Thread(target=db_thread, daemon=True)
    t_gui = threading.Thread(target=gui_thread)

    t_gps.start()
    t_db.start()
    t_gui.start()

    t_gui.join()


if __name__ == "__main__":
    main()
