from model.GPS_handler.gps_data import GPSData
import subprocess
from gps3 import gps3
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import copy


class GPSHandler:
    def __init__(self):
        self.gps_socket = None
        self.data_stream = None
        self.connected = False

    def run_command(self, cmd):

        try:
            print(f"Futtatás: {cmd}")
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.stdout:
                print("Output:", result.stdout.strip())
            if result.stderr:
                print("Hiba:", result.stderr.strip())
        except subprocess.CalledProcessError as e:
            print(f"Hiba a parancs futtatása közben: {cmd}")
            print(e.stderr)

    def initialize_gps(
        self, device="/dev/ttyACM0", ntrip_url="ntrip://crtk.net:2101/NEAR"
    ):
        self.device = device
        self.ntrip_url = ntrip_url
        # gpsd leállítása
        self.run_command("sudo systemctl stop gpsd.socket")
        self.run_command("sudo systemctl stop gpsd.service")
        self.run_command("sudo pkill gpsd")

        # gpsd elindítása NTRIP-kapcsolattal
        cmd = f"gpsd -nG {self.ntrip_url} {self.device}"
        self.run_command(cmd)
        print("GPS inicializálás kész.")

    def connect_to_gps(self):

        while not self.connected:
            try:
                self.gps_socket = gps3.GPSDSocket()
                self.data_stream = gps3.DataStream()
                self.gps_socket.connect(host="127.0.0.1", port=2947)
                self.gps_socket.watch(enable=True, gpsd_protocol="json")
                print("GPS kapcsolat létrejött.")
                self.connected = True  # sikeres csatlakozás
            except Exception as e:
                try:
                    self.close_gps_connection()
                except Exception as e:
                    print("Hiba történt a csatlakozás során:", e)
                self.initialize_gps()
                print("Újracsatlakozás a gpsd-hez 2 másodperc múlva...")
                time.sleep(2)

    def close_gps_connection(self):
        if self.gps_socket:
            try:
                self.gps_socket.close()
                self.run_command("sudo systemctl stop gpsd.socket")
                self.run_command("sudo systemctl stop gpsd.service")
                self.run_command("sudo pkill gpsd")

            except Exception as e:
                print("Hiba a GPS socket lezárásakor:", e)
            finally:
                print("GPS sikeresen lezárva!")
                self.gps_socket = None
                self.data_stream = None
                self.connected = False

    def gps_data_ms_to_km(self, gps_data):
        try:
            gps_data.speed = float(gps_data.speed) * 3.6
            gps_data.speed = round(gps_data.speed, 3)
        except (TypeError, ValueError):
            gps_data.speed = None

    def gps_data_time_to_bp(self, gps_data):
        gps_time_str = gps_data.time
        gps_time = None

        if gps_time_str and gps_time_str != "n/a":
            try:
                # ISO formátumú UTC idő beolvasása
                gps_time = datetime.fromisoformat(gps_time_str.replace("Z", "+00:00"))
                # Átváltás Budapest helyi időre
                gps_time = gps_time.astimezone(ZoneInfo("Europe/Budapest"))
                # Frissítjük az objektumban is
                gps_data.time = gps_time.isoformat(timespec="seconds")
            except Exception as e:
                print(f"Hiba az idő konvertálásakor: {e}")
                gps_data.time = None
                gps_time = None
        else:
            gps_data.time = None
            gps_time = None

    def get_gps_data(self, my_gps_data):
        
        gps_socket = gps3.GPSDSocket()
        data_stream = gps3.DataStream()

        gps_socket.connect(host='127.0.0.1', port=2947)   # vagy hagyd ki a paramétereket
        gps_socket.watch(enable=True, gpsd_protocol='json')
        
        best_lat = None
        best_lon = None
        best_lat_err = None
        best_lon_err = None
        
        altitudes = list()
        speeds = list()
        last_mode = None
        last_time_value = None
        avg_speed = 0.0
        
        RED = "\033[31m"
        GREEN = "\033[32m"
        RESET = "\033[0m"
        
        measure_start  = time.time()
        
        for new_data in gps_socket:
                if new_data:

                    data_stream.unpack(new_data)
                    tpv = data_stream.TPV  # Time-Position-Velocity objektum dict-szerűen
                    lat = tpv.get('lat', None)
                    lon = tpv.get('lon', None)
                    alt = tpv.get('alt', None)
                    speed = tpv.get('speed', None)   # m/s
                    mode = tpv.get('mode', 0)        # 0/1=no fix, 2=2D, 3=3D
                    time_gps = tpv.get('time', None)
                    latitude_error = tpv.get("epy")
                    longitude_error = tpv.get("epx")
                    
                    latitude_error = tpv.get("epy", None)
                    longitude_error = tpv.get("epx", None)

                    # Kényszerítés float típusra, ha nem None
                    try:
                        latitude_error = float(latitude_error) if latitude_error is not None else float('inf')
                    except ValueError:
                        latitude_error = float('inf')

                    try:
                        longitude_error = float(longitude_error) if longitude_error is not None else float('inf')
                    except ValueError:
                        longitude_error = float('inf')
                        
                    #print(f"lat = {lat} lon = {lon}")
                    
                
                    if time.time() - measure_start  >= 5.0:  
                        my_gps_data.latitude = copy.deepcopy(best_lat)
                        my_gps_data.longitude = copy.deepcopy(best_lon)
                        my_gps_data.latitude_error = copy.deepcopy(best_lat_err)
                        my_gps_data.longitude_error = copy.deepcopy(best_lon_err)
                        my_gps_data.time = copy.deepcopy(time_gps)
                        my_gps_data.speed = copy.deepcopy(avg_speed)
                        my_gps_data.mode = f"fix:{'3D' if mode==3 else '2D' if mode==2 else 'no'}" 
                        self.gps_data_ms_to_km(my_gps_data) 
                        self.gps_data_time_to_bp(my_gps_data)
                        measure_start= time.time()          
                        best_lat = None
                        best_lon = None
                        best_lat_err = None
                        best_lon_err = None
                        speeds = []
                        altitudes = []
                        avg_speed = 0.0   
                        my_gps_data.measure_fixed = True
                        print(f"{RED}Frissítés{RESET}")
                        
                    else:   
                        my_gps_data.measure_fixed = False
                        try:
                            s = float(speed)
                            speeds.append(s)
                        except (TypeError, ValueError):
                            pass
                        
                        sum_speed = 0.0
                        
                        for i, elem in enumerate(speeds):
                            sum_speed = sum_speed + elem

                        avg_speed = speed
                        
                        
                        if best_lat is None and best_lat_err is None:
                            #print(f"Lon es lon_err inicializalas lat= {lat} lat_err= {latitude_error}")
                            best_lat = lat
                            best_lat_err = latitude_error
                        
                        if best_lon is None and best_lon_err is None:
                            #print(f"Lon es lon_err inicializalas lon= {lon} lat= {longitude_error}")
                            best_lon = lon
                            best_lon_err = longitude_error
                            
                        if latitude_error < best_lat_err:
                            #print(f"{GREEN}talalt jobb szelesseget: {lat}{RESET}")
                            best_lat_err = latitude_error
                            best_lat = lat
                        
                        if longitude_error < best_lon_err:
                            #print(f"{GREEN}talalt jobb hosszusagot: {lon}{RESET}")
                            best_lon_err = longitude_error
                            best_lon = lon

                    """my_gps_data.latitude = copy.deepcopy(best_lat)
                    my_gps_data.longitude = copy.deepcopy(best_lon)
                    my_gps_data.latitude_error = best_lat_err
                    my_gps_data.longitude_error = best_lon_err
                    my_gps_data.time = time_gps
                    my_gps_data.speed = avg_speed
                    my_gps_data.mode = f"fix:{'3D' if mode==3 else '2D' if mode==2 else 'no'}" 
                    self.gps_data_ms_to_km(my_gps_data) 
                    self.gps_data_time_to_bp(my_gps_data)"""
