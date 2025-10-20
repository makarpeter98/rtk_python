from gps_data import GPSData
import subprocess
from gps3 import gps3
import time


class GPSHandler:
    def __init__(self):
        self.gps_socket = None
        self.data_stream = None
        self.connected = False

    def run_command(self, cmd):
        """
        Segédfüggvény a parancs futtatásához és hibakezeléshez
        """
        try:
            print(f"Futtatás: {cmd}")
            result = subprocess.run(
                cmd, shell=True, check=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.stdout:
                print("Output:", result.stdout.strip())
            if result.stderr:
                print("Hiba:", result.stderr.strip())
        except subprocess.CalledProcessError as e:
            print(f"Hiba a parancs futtatása közben: {cmd}")
            print(e.stderr)

    def initialize_gps(self, device="/dev/ttyACM0", ntrip_url="ntrip://crtk.net:2101/NEAR"):
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
        """
        Csatlakozás a gpsd-hez és TPV adatok kiolvasása
        Addig próbálkozik, amíg a kapcsolat létrejön.
        """
        while not self.connected:
            try:
                self.gps_socket = gps3.GPSDSocket()
                self.data_stream = gps3.DataStream()
                self.gps_socket.connect(host='127.0.0.1', port=2947)
                self.gps_socket.watch(enable=True, gpsd_protocol='json')
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
            except Exception as e:
                print("Hiba a GPS socket lezárásakor:", e)
            finally:
                self.gps_socket = None
                self.data_stream = None
                self.connected = False

from gps_data import GPSData
import subprocess
from gps3 import gps3
import time


class GPSHandler:
    def __init__(self):
        self.gps_socket = None
        self.data_stream = None
        self.connected = False

    def run_command(self, cmd):
        """
        Segédfüggvény a parancs futtatásához és hibakezeléshez
        """
        try:
            print(f"Futtatás: {cmd}")
            result = subprocess.run(
                cmd, shell=True, check=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.stdout:
                print("Output:", result.stdout.strip())
            if result.stderr:
                print("Hiba:", result.stderr.strip())
        except subprocess.CalledProcessError as e:
            print(f"Hiba a parancs futtatása közben: {cmd}")
            print(e.stderr)

    def initialize_gps(self, device="/dev/ttyACM0", ntrip_url="ntrip://crtk.net:2101/NEAR"):
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
        """
        Csatlakozás a gpsd-hez és TPV adatok kiolvasása
        Addig próbálkozik, amíg a kapcsolat létrejön.
        """
        while not self.connected:
            try:
                self.gps_socket = gps3.GPSDSocket()
                self.data_stream = gps3.DataStream()
                self.gps_socket.connect(host='127.0.0.1', port=2947)
                self.gps_socket.watch(enable=True, gpsd_protocol='json')
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

    def get_gps_data(self, gps_data):
        # print("GPS adatok szolgáltatása.")
            
        for new_data in self.gps_socket:
            if new_data:
                self.data_stream.unpack(new_data)
                tpv = self.data_stream.TPV  # Time-Position-Velocity objektum dict-szerűen
                lat = tpv.get('lat', None)
                lon = tpv.get('lon', None)
                alt = tpv.get('alt', None)
                speed = tpv.get('speed', None)   # m/s
                mode = tpv.get('mode', 0)        # 0/1=no fix, 2=2D, 3=3D
                timefix = tpv.get('time', None)
                lat_err = tpv.get('epy', None)
                lon_err = tpv.get('epx', None)

                #print(f"mode={mode} lat={lat} lon={lon} lon_err={lon_err} lat_err={lat_err} speed={speed}")
                #print(f"lat_len={len(lat)} lon_len={len(lon)}")
                
                if (
                    lat is not None and lon is not None and
                    lat_err is not None and lon_err is not None and
                    lat != "n/a" and lon != "n/a" 
                    ):
                        gps_data.longitude = lon
                        gps_data.latitude = lat
                        gps_data.longitude_error = lon_err
                        gps_data.latitude_error = lat_err
                        gps_data.speed = speed
                        break
                

            time.sleep(0.1)

                




