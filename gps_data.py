from gps3 import gps3
import time

class GPSData:
	def __init__(self):
		self.longitude = None
		self.latitude = None
		self.longitude_error = None
		self.latitude_error = None
		self.speed = None
		


"""

for new_data in gps_socket:
                    if not new_data:
                        continue
                    data_stream.unpack(new_data)
                    tpv = data_stream.TPV
                    
                    lat = tpv.get('lat', None)
                    lon = tpv.get('lon', None)
                    mode = tpv.get('mode', 0)

                    # TPV hibák / pontosságok
                    epx = tpv.get('epx', None)        # longitude error (m)
                    epy = tpv.get('epy', None)        # latitude error (m)
                    epv = tpv.get('epv', None)        # altitude error (m) – ha nem kell, hagyhatod
                    ept = tpv.get('ept', None)        # time error (s)
                    geoid_sep = tpv.get('geoidSep', None)
                    satellites_used = tpv.get('satellites_used', None)

                    timefix = tpv.get('time', None)
                    
                    # mode int típusra konvertálása
                    try:
                        mode = int(mode)
                    except (ValueError, TypeError):
                        mode = 0

                    # Csak érvényes fix esetén írjuk ki
                    if mode >= 2:
                        print(f"lat={lat} lat_err={epy} lon={lon} lon_err={epx}")
                    else:
                        print("Nincs megfelelő mennyiségű vagy minőségű adat!")
                    
                    time.sleep(3);


"""
