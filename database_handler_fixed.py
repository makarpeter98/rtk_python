import sqlite3

class DataBaseHandler:
    
    def __init__(self):
        self.conn = sqlite3.connect("gps_data.db")
        self.cursor = conn.cursor()
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS gps_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            latitude REAL,
            longitude REAL,
            latitude_error REAL,
            longitude_error REAL,
            speed REAL
        )
    """)

        self.conn.commit()
        self.conn.close()

    def save_gps_data(gps_data):
        self.conn = sqlite3.connect("gps_data.db")
        self.cursor = conn.cursor()

        self.cursor.execute("""
            INSERT INTO gps_log (latitude, longitude, latitude_error, longitude_error, speed)
            VALUES (?, ?, ?, ?, ?)
        """, (
            gps_data.latitude,
            gps_data.longitude,
            gps_data.latitude_error,
            gps_data.longitude_error,
            gps_data.speed
        ))

        self.conn.commit()
        self.conn.close()
        
    def read_last_gps_data():
        self.conn = sqlite3.connect("gps_data.db")
        self.cursor = conn.cursor()

        self.cursor.execute("SELECT * FROM gps_log ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

        self.conn.close()
        return result

