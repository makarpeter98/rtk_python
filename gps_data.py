from gps3 import gps3
import time

class GPSData:
	def __init__(self):
		self.longitude = None
		self.latitude = None
		self.longitude_error = None
		self.latitude_error = None
		self.mode = None
		self.speed = None
		self.comment = None
		
