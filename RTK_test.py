# gps3_example.py
from gps3 import gps3
import time

gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()

gps_socket.connect(host='127.0.0.1', port=2947)   # vagy hagyd ki a paramétereket
gps_socket.watch(enable=True, gpsd_protocol='json')

for new_data in gps_socket:
    if new_data:
        data_stream.unpack(new_data)
        tpv = data_stream.TPV  # Time-Position-Velocity objektum dict-szerűen
        lat = tpv.get('lat', None)
        lon = tpv.get('lon', None)
        alt = tpv.get('alt', None)
        speed = tpv.get('speed', None)   # m/s
        mode = tpv.get('mode', 0)        # 0/1=no fix, 2=2D, 3=3D
        timefix = tpv.get('time', None)

        print(f"mode={mode} lat={lat} lon={lon} alt={alt} speed={speed} time={timefix}")

    time.sleep(0.1)
    
    
""" 

cat /dev/ttyACM0
cgps -s
sudo systemctl stop gpsd.socket
sudo systemctl stop gpsd.service
sudo pkill gpsd
gpsd -nG ntrip://crtk.net:2101/NEAR /dev/ttyACM0

sudo systemctl daemon-reload










"""

