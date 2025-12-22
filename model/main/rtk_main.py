import threading
import queue
import time
import argparse
import sys
import copy

from model.GPS_handler.gps_handler import GPSHandler, GPSData
from model.DB_handler.database_handler import DataBaseHandler
from viewcontroller.Main_GUI.gui_handler_main import GUIHandler
from model.Socket_handler.socket_handler import SocketHandler

# --- Megosztott objektumok ---
my_gps_data = GPSData()
my_gps_data_list = list()
gps_lock = threading.Lock()
save_queue = queue.Queue()
stop_event = threading.Event()

my_gps_handler = None


def add_my_gps_data_to_my_gps_data_list():
    global my_gps_data
    global my_gps_data_list
    
    print(f"GPS Adat a listához adva! {len(my_gps_data_list)}")
    tmp_gps_data = copy.deepcopy(my_gps_data)
    my_gps_data_list.append(tmp_gps_data)


def clear_gps_data_list():
    my_gps_data_list.clear()


def print_all_gps_data():
    global my_gps_data
    print(
        f"  GPS adatok\n"
        f"  Szélesség:          {my_gps_data.latitude} fok\n"
        f"  Hosszúság:          {my_gps_data.longitude} fok\n"
        f"  Szélességi hiba:    {my_gps_data.latitude_error}m\n"
        f"  Hosszúsági hiba:    {my_gps_data.longitude_error}m\n"
        f"  Sebesség:           {my_gps_data.speed}km/h\n"
        f"  Mód:                {my_gps_data.mode}\n"
        f"  Megjegyzés:         {my_gps_data.comment}\n"
        f"  Idő:                {my_gps_data.time}\n"
        f"  GPS pont mentése:   {my_gps_data.store_gps_data}\n"
    )


def store_gps_data():
    global my_gps_data

    print("GPS adat mentése adatbázisba...")

    # 1) Mentés az adatbázisba
    db = DataBaseHandler()
    db.save_gps_data(my_gps_data)

    # 2) Komment visszaállítása
    my_gps_data.comment = ""

    # 3) Flag visszaállítása
    my_gps_data.store_gps_data = False

    print("Mentés kész!")



def on_measure_fixed():
    """
    EGYETLEN callback, amit a GPSData.measure_fixed hív:
    - mindig kiír
    - mindig listába rak
    - ha store_gps_data == True, akkor ment
    """
    print_all_gps_data()
    add_my_gps_data_to_my_gps_data_list()

    if my_gps_data.store_gps_data:
        store_gps_data()


def gps_thread():
    global my_gps_data
    my_gps_handler = GPSHandler()
    print("gps_thread elindult")
    my_gps_handler.get_gps_data(my_gps_data)
    my_gps_handler.close_gps_connection()


def socket_thread():
    socket_handler = SocketHandler(stop_event, my_gps_data, gps_lock, save_queue)
    socket_handler.start_server()


def start_gui():
    global my_gps_data
    gui_handler = GUIHandler(gps_lock, my_gps_data, my_gps_data_list, clear_gps_data_list)
    gui_handler.run()


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

    threading.Thread(target=gps_thread, daemon=True).start()
    threading.Thread(target=socket_thread, daemon=True).start()

    # Egyetlen measure_fixed callback
    my_gps_data.add_fixed_callback(on_measure_fixed)

    start_gui()

    stop_event.set()
    print("Program vége")


if __name__ == "__main__":
    main()
