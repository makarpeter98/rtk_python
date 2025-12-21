import threading
import queue
import time
import tkinter as tk
import argparse
import sys

from model.GPS_handler.gps_handler import GPSHandler
from model.GPS_handler.gps_handler import GPSData
from model.DB_handler.database_handler import DataBaseHandler
from viewcontroller.Main_GUI.gui_handler_main import GUIHandler
from model.Socket_handler.socket_handler import SocketHandler
from viewcontroller.Graphing.gps_graph_gui import GPSGraphGUI

# --- Csak a hibakiírások (stderr) elnyomása ---
class DevNull:
    def write(self, msg):
        pass
    def flush(self):
        pass



# --- Megosztott objektumok ---
my_gps_data = GPSData()
gps_lock = threading.Lock()
save_queue = queue.Queue()
stop_event = threading.Event()  # Mutable stop jelzés
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"

my_gps_handler = None        

def print_all_gps_data(my_gps_data):
    print(
                f"  GPS adatok\n"
                f"  Szélesség:       {my_gps_data.latitude} fok\n"
                f"  Hosszúság:       {my_gps_data.longitude} fok\n"
                f"  Szélességi hiba: {my_gps_data.latitude_error}m\n"
                f"  Hosszúsági hiba: {my_gps_data.longitude_error}m\n"
                f"  Sebesség:        {my_gps_data.speed}km/h\n"
                f"  Mód:             {my_gps_data.mode}\n"
                f"  Megjegyzés:      {my_gps_data.comment}\n"
                f"  Idő:             {my_gps_data.time}\n"
            )

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
    
def start_Graph_GUI():
    global my_gps_data
    graph_gui = GPSGraphGUI(gps_lock, my_gps_data)
    graph_gui.run()

    

# --- Fő program ---
def main():
    parser = argparse.ArgumentParser(description="RTK GUI + GPS")
    parser.add_argument("-i", "--init", type=str, required=True)
    parser.add_argument("-oi", "--only_init", type=str)
    #parser.add_argument("--graph", action="store_true", help="Indítsa el a GPS grafikon GUI-t")
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
    #threading.Thread(target=start_Graph_GUI, daemon=True).start()
    
    #sys.stderr = DevNull()  # Exception-ök és hibák nem fognak látszódni
    my_gps_data.add_callback(print_all_gps_data)
    # GUI fő szálon
    start_gui()

    # GUI bezárás után stop jelzés
    stop_event.set()
    print("Program vége")


if __name__ == "__main__":
    main()
