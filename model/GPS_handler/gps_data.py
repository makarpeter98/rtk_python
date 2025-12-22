from gps3 import gps3
import time

class GPSData:
    def __init__(self):
        self._measure_fixed = False
        self._fixed_callbacks = []

        self.latitude = 0.0
        self.longitude = 0.0
        self.speed = 0.0
        self.latitude_error = 0.0
        self.longitude_error = 0.0
        self.mode = ""
        self.comment = ""
        self.time = None

        # Csak egy flag, nem callback-eltet
        self._store_gps_data = False

    @property
    def measure_fixed(self):
        return self._measure_fixed

    @measure_fixed.setter
    def measure_fixed(self, value):
        # Ha most lett fix először
        if value and not self._measure_fixed:
            for cb in self._fixed_callbacks:
                cb()
        self._measure_fixed = value

    @property
    def store_gps_data(self):
        return self._store_gps_data

    @store_gps_data.setter
    def store_gps_data(self, value):
        # Csak a flaget állítjuk, nincs callback
        self._store_gps_data = value

    def add_fixed_callback(self, func):
        if callable(func):
            self._fixed_callbacks.append(func)
