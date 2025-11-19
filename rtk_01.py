import threading
import queue
import time
import tkinter as tk
import argparse

from gps_handler import GPSHandler
from gps_data import GPSData
from database_handler import DataBaseHandler
from gui_handler import GUIHandler
from socket_handler import SocketHandler

# --- Megosztott objektumok ---
my_gps_data = GPSData()
gps_lock = threading.Lock()
save_queue = queue.Queue()
stop_event = threading.Event()  # Mutable stop jelzés

my_gps_handler = None

def test_thread():
    
    global my_gps_data
    
    print("Test thread elindult")
    
    while True:
        print(f"lat={my_gps_data.latitude} lon={my_gps_data.longitude} speed= {my_gps_data.speed}")
        time.sleep(1.5)

# --- GPS szál ---
def gps_thread():
    global my_gps_data
    my_gps_handler = GPSHandler()
    #my_gps_handler.connect_to_gps()
    print("gps_thread elindult")
    
    
    while not stop_event.is_set():
        my_gps_data = GPSData()
        my_gps_handler.get_gps_data(my_gps_data)
        print(f"ido= {time.time() - measure_start}")
    
    my_gps_handler.close_gps_connection()

# --- DB szál ---
def db_thread():
    db_handler = DataBaseHandler()
    while not stop_event.is_set():
        try:
            save_queue.get(timeout=0.5)
        except queue.Empty:
            continue

        with gps_lock:
            if not my_gps_data.comment:
                my_gps_data.comment = None
            db_handler.save_gps_data(my_gps_data)
            print(f"db_thread: Mentve: lat={my_gps_data.latitude}, lon={my_gps_data.longitude}, comment={my_gps_data.comment}")

        save_queue.task_done()

# --- Socket szál ---
def socket_thread():
    socket_handler = SocketHandler(stop_event, my_gps_data, gps_lock, save_queue)
    socket_handler.start_server()

# --- GUI ---
def start_gui():
    global my_gps_data
    gui_handler = GUIHandler(save_queue, gps_lock, my_gps_data)
    gui_handler.run()  # mainloop fő szálon

# --- Fő program ---
def main():
    parser = argparse.ArgumentParser(description="RTK GUI + GPS")
    parser.add_argument("-i", "--init", type=str, required=True)
    parser.add_argument("-oi", "--only_init", type=str)
    args = parser.parse_args()

    if args.init == "True":
        GPSHandler().initialize_gps()
    if args.only_init == "True":
        print("Csak inicializálás, kilépés...")
        return

    # Szálak indítása
    threading.Thread(target=gps_thread, daemon=True).start()
    threading.Thread(target=db_thread, daemon=True).start()
    threading.Thread(target=socket_thread, daemon=True).start()
    threading.Thread(target=test_thread, daemon=True).start()

    # GUI fő szálon
    start_gui()

    # GUI bezárás után stop jelzés
    stop_event.set()
    print("Program vége")


if __name__ == "__main__":
    main()
