import sqlite3

class DataBaseHandler:
    
    def __init__(self):
        self.conn = sqlite3.connect("gps_data.db")
        self.cursor = self.conn.cursor()
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS gps_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            latitude REAL,
            longitude REAL,
            latitude_error REAL,
            longitude_error REAL,
            speed REAL,
            mode TEXT,
            comment TEXT
        )""")

        self.conn.commit()
        self.conn.close()

    def save_gps_data(self, gps_data):
        self.conn = sqlite3.connect("gps_data.db")
        self.cursor = self.conn.cursor()

        print(f"Mentés: time={gps_data.time} lat={gps_data.latitude} lon={gps_data.longitude} lat_err={gps_data.latitude_error} lon_err={gps_data.longitude_error} speed={gps_data.speed} mode={gps_data.mode} comment={gps_data.comment}")

        self.cursor.execute("""
            INSERT INTO gps_log (timestamp, latitude, longitude, latitude_error, longitude_error, speed, mode, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            gps_data.time or 0.0,
            gps_data.latitude or 0.0,
            gps_data.longitude or 0.0,
            gps_data.latitude_error or 0.0,
            gps_data.longitude_error or 0.0,
            gps_data.speed or 0.0,
            gps_data.mode or None,
            gps_data.comment or None
        ))

        self.conn.commit()
        self.conn.close()
        
    def read_last_gps_data(self):
        """Lekéri az utolsó mentett GPS adatot."""
        self.conn = sqlite3.connect("gps_data.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT * FROM gps_log ORDER BY id DESC LIMIT 1")
        result = self.cursor.fetchone()

        self.conn.close()
        return result
