from gps_data import GPSData
import subprocess
from gps3 import gps3
import time
from datetime import datetime
from zoneinfo import ZoneInfo


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

    def initialize_gps( self, device="/dev/ttyACM0", ntrip_url="ntrip://crtk.net:2101/NEAR" ):
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
            gps_data.speed  = round(gps_data.speed, 3)
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
                gps_data.time = gps_time.isoformat(timespec='seconds')
            except Exception as e:
                print(f"Hiba az idő konvertálásakor: {e}")
                gps_data.time = None
                gps_time = None
        else:
            gps_data.time = None
            gps_time = None

    
    def get_gps_data(self):
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        """Visszaad egy GPSData objektumot, ha van új TPV adat, különben None"""
        for new_data in self.gps_socket:
            if new_data:
                self.data_stream.unpack(new_data)
                tpv = self.data_stream.TPV
                lat = tpv.get("lat")
                lon = tpv.get("lon")
                latitude_error = tpv.get("epy")
                longitude_error = tpv.get("epx")
                time = tpv.get("time", None)
                speed = tpv.get("speed", None)
                mode = tpv.get("mode", 0)
                
                gps_data = GPSData()
                gps_data.latitude = lat
                gps_data.longitude = lon
                gps_data.latitude_error = latitude_error
                gps_data.longitude_error = longitude_error
                gps_data.time = time
                gps_data.speed = speed
                gps_data.mode = f"fix:{'3D' if mode==3 else '2D' if mode==2 else 'no'}"
                
                self.gps_data_ms_to_km(gps_data)
                self.gps_data_time_to_bp(gps_data)
                
                print(f"lon = {lon} lat={lat} time={gps_data.time}")
                
                return gps_data
