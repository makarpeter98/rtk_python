from model.GPS_handler.gps_data import GPSData
from gps3 import gps3
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import copy


def safe_float(value, default=float('inf')):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class GPSHandler:
    def __init__(self, gps_list):
        self.gps_list = gps_list

        # Dinamikus időzítések
        self.normal_measure_time = 0.5     # másodperc
        self.long_measure_time = 5   # másodperc

    def gps_data_ms_to_km(self, gps_data):
        try:
            gps_data.speed = float(gps_data.speed) * 3.6
            gps_data.speed = round(gps_data.speed, 3)
        except:
            gps_data.speed = None

    def gps_data_time_to_bp(self, gps_data):
        gps_time_str = gps_data.time
        if gps_time_str and gps_time_str != "n/a":
            try:
                gps_time = datetime.fromisoformat(gps_time_str.replace("Z", "+00:00"))
                gps_time = gps_time.astimezone(ZoneInfo("Europe/Budapest"))
                gps_data.time = gps_time.isoformat(timespec="seconds")
            except:
                gps_data.time = None
        else:
            gps_data.time = None

    def get_gps_data(self, my_gps_data):

        gps_socket = gps3.GPSDSocket()
        data_stream = gps3.DataStream()

        gps_socket.connect(host='127.0.0.1', port=2947)
        gps_socket.watch(enable=True, gpsd_protocol='json')

        # Állapotok
        big_mode = False
        measure_start = None

        # Normál mérés időzítése
        last_normal_measure = 0

        # Nagy méréshez szükséges változók
        best_lat = None
        best_lon = None
        best_lat_err = None
        best_lon_err = None
        speeds = []
        avg_speed = 0.0

        while True:
            for new_data in gps_socket:
                if not new_data:
                    continue

                data_stream.unpack(new_data)
                tpv = data_stream.TPV

                lat = tpv.get('lat')
                lon = tpv.get('lon')
                speed = tpv.get('speed')
                time_gps = tpv.get('time')
                mode = tpv.get('mode', 0)

                latitude_error = safe_float(tpv.get("epy"))
                longitude_error = safe_float(tpv.get("epx"))

                # Gombnyomás → nagy mérés indul
                if my_gps_data.store_gps_data and not big_mode:
                    print(f">>> Nagy mérés indul ({self.long_measure_time} másodperc)")
                    big_mode = True
                    measure_start = time.time()

                    best_lat = lat
                    best_lon = lon
                    best_lat_err = latitude_error
                    best_lon_err = longitude_error
                    speeds = []
                    avg_speed = 0.0
                    continue

                # Nagy mérés fut
                if big_mode:

                    # hosszú mérés lezárása
                    if time.time() - measure_start >= self.long_measure_time:

                        my_gps_data.latitude = best_lat
                        my_gps_data.longitude = best_lon
                        my_gps_data.latitude_error = best_lat_err
                        my_gps_data.longitude_error = best_lon_err
                        my_gps_data.time = time_gps
                        my_gps_data.speed = avg_speed
                        my_gps_data.mode = f"fix:{'3D' if mode == 3 else '2D' if mode == 2 else 'no'}"

                        self.gps_data_ms_to_km(my_gps_data)
                        self.gps_data_time_to_bp(my_gps_data)

                        my_gps_data.measure_fixed = True
                        print(f">>> Nagy mérés kész ({self.long_measure_time} másodperc)")

                        # callback majd menti
                        my_gps_data.store_gps_data = False

                        # visszaállunk normál módba
                        big_mode = False
                        measure_start = None
                        continue

                    # nagy mérés közben adatgyűjtés
                    my_gps_data.measure_fixed = False

                    try:
                        speeds.append(float(speed))
                        avg_speed = sum(speeds) / len(speeds)
                    except:
                        pass

                    if latitude_error < best_lat_err:
                        best_lat_err = latitude_error
                        best_lat = lat

                    if longitude_error < best_lon_err:
                        best_lon_err = longitude_error
                        best_lon = lon

                    continue

                # Normál mód (1 mp-es mérés)
                if not big_mode:
                    if time.time() - last_normal_measure >= self.normal_measure_time:
                        last_normal_measure = time.time()

                        my_gps_data.latitude = lat
                        my_gps_data.longitude = lon
                        my_gps_data.latitude_error = latitude_error
                        my_gps_data.longitude_error = longitude_error
                        my_gps_data.time = time_gps
                        my_gps_data.speed = speed
                        my_gps_data.mode = f"fix:{'3D' if mode == 3 else '2D' if mode == 2 else 'no'}"

                        self.gps_data_ms_to_km(my_gps_data)
                        self.gps_data_time_to_bp(my_gps_data)

                        my_gps_data.measure_fixed = False

                        # Normál mérés hozzáadása a grafikon listához
                        self.gps_list.append(copy.deepcopy(my_gps_data))

                        print(f"Normál mérés ({self.normal_measure_time} másodperc)")
