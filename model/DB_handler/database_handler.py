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
        RED = "\033[31m"
        GREEN = "\033[32m"
        RESET = "\033[0m"
        
        # Szép formázott log
        print(
            f"    {GREEN}Mentés!{RESET}\n"
            f"    Idő:              {gps_data.time}\n"
            f"    Szélesség:        {gps_data.latitude}\n"
            f"    Hosszúság:        {gps_data.longitude}\n"
            f"    Sebesség:         {gps_data.speed} km/h\n"
            f"    Mérési mód:       {gps_data.mode}\n"
            f"    Komment:          {gps_data.comment}\n"
            f"    Mérési iteráció:  {measurement_iteration}\n"
            f"    Mérési pont:      {measurement_point}\n"
            f"    GPS pont mentése: {gps_data.store_gps_data}\n"
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
        
        gps_data.store_gps_data = False
        
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
        
    def get_all_gps_data(self):
        """Visszaadja az összes GPS adatot GPSData objektumok listájaként."""
        from model.GPS_handler.gps_handler import GPSData  # lokális import, hogy elkerüljük a körkört

        self.conn = sqlite3.connect("gps_data.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT * FROM gps_log ORDER BY id ASC")
        rows = self.cursor.fetchall()
        self.conn.close()

        gps_list = []

        for row in rows:
            (
                _id,
                timestamp,
                latitude,
                longitude,
                latitude_error,
                longitude_error,
                speed,
                mode,
                measurement_iteration,
                measurement_point,
                comment
            ) = row

            gps = GPSData()
            gps.time = timestamp
            gps.latitude = latitude
            gps.longitude = longitude
            gps.latitude_error = latitude_error
            gps.longitude_error = longitude_error
            gps.speed = speed
            gps.mode = mode

            # A comment mezőt visszaállítjuk eredeti formára
            if measurement_iteration is not None and measurement_point is not None:
                if comment:
                    gps.comment = f"{measurement_iteration}/{measurement_point}/{comment}"
                else:
                    gps.comment = f"{measurement_iteration}/{measurement_point}"
            else:
                gps.comment = comment or ""

            gps_list.append(gps)

        return gps_list
        
    def delete_gps_data_from_db(self, lat, lon):
        """Töröl egy GPS pontot az adatbázisból a koordináták alapján."""
        self.conn = sqlite3.connect("gps_data.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            DELETE FROM gps_log
            WHERE latitude = ? AND longitude = ?
        """, (lat, lon))

        self.conn.commit()
        self.conn.close()

        
    def delete_all_gps_data_from_db(self):
        """Törli az összes GPS adatot az adatbázisból."""
        self.conn = sqlite3.connect("gps_data.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("DELETE FROM gps_log")

        self.conn.commit()
        self.conn.close()

        

