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
            measurement_iteration INTEGER,
            measurement_point INTEGER,
            comment TEXT
        )""")
        self.conn.commit()
        self.conn.close()

    def save_gps_data(self, gps_data):
        self.conn = sqlite3.connect("gps_data.db")
        self.cursor = self.conn.cursor()

        # Kinyerjük az iterációt és a pontot a comment mezőből
        measurement_iteration = None
        measurement_point = None
        comment_text = None
        comment = gps_data.comment
        
        try:
            parts = comment.split("/", 2)  # maximum 3 részre bontjuk
            if len(parts) >= 2:
                measurement_iteration = int(parts[0])
                measurement_point = int(parts[1])
            if len(parts) == 3:
                comment_text = parts[2]
                gps_data.comment = comment_text
        except (ValueError, AttributeError):
            print("Hibás formátum a comment mezőben:", comment)
            
        # Szép formázott log
        print(
            f"db_handler:\n"
            f"  Mentés:\n"
            f"    Time:  {gps_data.time}\n"
            f"    Lat:   {gps_data.latitude}\n"
            f"    Lon:   {gps_data.longitude}\n"
            f"    Speed: {gps_data.speed} km/h\n"
            f"    Mode:  {gps_data.mode}\n"
            f"    Comment: {gps_data.comment}\n"
            f"    Iteráció: {measurement_iteration}\n"
            f"    Pont: {measurement_point}\n"
            f"    Comment: {gps_data.comment}\n"
        )

        # Mentés az adatbázisba
        self.cursor.execute("""
            INSERT INTO gps_log (
                timestamp, latitude, longitude, latitude_error, longitude_error, speed, mode,
                measurement_iteration, measurement_point, comment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            getattr(gps_data, "time", 0.0),
            getattr(gps_data, "latitude", 0.0),
            getattr(gps_data, "longitude", 0.0),
            getattr(gps_data, "latitude_error", 0.0),
            getattr(gps_data, "longitude_error", 0.0),
            getattr(gps_data, "speed", 0.0),
            getattr(gps_data, "mode", None),
            measurement_iteration,
            measurement_point,
            comment
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
