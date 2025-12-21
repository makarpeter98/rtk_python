from gps3 import gps3
import time

class GPSData:
    def __init__(self):
        self._measure_fixed = False
        self._callbacks = []  # ide tesszük a figyelőket
        self.latitude = 0.0
        self.longitude = 0.0
        self.speed = 0.0
        self.latitude_error = 0.0
        self.longitude_error = 0.0
        self.mode = ""
        self.comment = ""
        self.time = None

    @property
    def measure_fixed(self):
        return self._measure_fixed

    @measure_fixed.setter
    def measure_fixed(self, value):
        if value and not self._measure_fixed:  # csak False -> True váltásnál
            for callback in self._callbacks:
                callback(self)  # hívjuk a callback-eket, átadjuk az objektumot
        self._measure_fixed = value

    def add_callback(self, func):
        """Feliratkoztatunk egy callback-et"""
        if callable(func):
            self._callbacks.append(func)
