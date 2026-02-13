import threading
import queue
import argparse
import copy

from model.GPS_handler.gps_handler import GPSHandler
from model.GPS_handler.gps_data import GPSData
from model.DB_handler.database_handler import DataBaseHandler
from viewcontroller.Main_GUI.gui_handler_main import GUIHandler
from model.Socket_handler.socket_handler import SocketHandler

my_gps_data = GPSData()
my_gps_data_list = []
gps_lock = threading.Lock()
save_queue = queue.Queue()
stop_event = threading.Event()


def add_my_gps_data_to_my_gps_data_list():
    tmp = copy.deepcopy(my_gps_data)
    my_gps_data_list.append(tmp)


def clear_gps_data_list():
    my_gps_data_list.clear()


def print_all_gps_data():
    print(
        f"GPS adatok:\n"
        f"  Lat: {my_gps_data.latitude}\n"
        f"  Lon: {my_gps_data.longitude}\n"
        f"  Lat err: {my_gps_data.latitude_error}\n"
        f"  Lon err: {my_gps_data.longitude_error}\n"
        f"  Speed: {my_gps_data.speed}\n"
        f"  Mode: {my_gps_data.mode}\n"
        f"  Time: {my_gps_data.time}\n"
        f"  Comment: {my_gps_data.comment}\n"
    )


def store_gps_data():
    print("GPS adat mentése adatbázisba...")
    db = DataBaseHandler()
    db.save_gps_data(my_gps_data)
    my_gps_data.comment = ""
    my_gps_data.store_gps_data = False
    print("Mentés kész!")


def on_measure_fixed():
    print_all_gps_data()
    add_my_gps_data_to_my_gps_data_list()

    if my_gps_data.store_gps_data:
        store_gps_data()


def gps_thread():
    gps_handler = GPSHandler(my_gps_data_list)
    gps_handler.get_gps_data(my_gps_data)


def socket_thread():
    socket_handler = SocketHandler(stop_event, my_gps_data, gps_lock, save_queue)
    socket_handler.start_server()


def start_gui():
    gui_handler = GUIHandler(gps_lock, my_gps_data, my_gps_data_list, clear_gps_data_list)
    gui_handler.run()


def main():
    parser = argparse.ArgumentParser(description="RTK GUI + GPS")
    parser.add_argument("-i", "--init", type=str, required=True)
    parser.add_argument("-oi", "--only_init", type=str)
    args = parser.parse_args()

    if args.only_init == "True":
        print("Csak inicializálás, kilépés...")
        return

    threading.Thread(target=gps_thread, daemon=True).start()
    threading.Thread(target=socket_thread, daemon=True).start()

    my_gps_data.add_fixed_callback(on_measure_fixed)

    start_gui()

    stop_event.set()
    print("Program vége")


if __name__ == "__main__":
    main()
