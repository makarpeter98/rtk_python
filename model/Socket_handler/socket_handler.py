import socket
import threading
import json

class SocketHandler:
    def __init__(self, stop_event, my_gps_data, gps_lock, save_queue):
        self.stop_event = stop_event
        self.my_gps_data = my_gps_data
        self.gps_lock = gps_lock
        self.save_queue = save_queue
        self.HOST = ""
        self.PORT = 5000

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.HOST, self.PORT))
        server_socket.listen(5)
        server_socket.settimeout(1.0)

        print(f"Szerver elindítva a {self.PORT}-as porton...")

        try:
            while not self.stop_event.is_set():
                try:
                    conn, addr = server_socket.accept()
                except socket.timeout:
                    continue

                threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr),
                    daemon=True
                ).start()

        finally:
            server_socket.close()
            print("Szerver lezárva.")

    def handle_client(self, conn, addr):
        print(f"Kapcsolódott: {addr}")

        with conn:
            with conn.makefile('r') as f:
                for line in f:
                    if not line:
                        break

                    try:
                        data = json.loads(line.strip())
                        event = data.get("event")
                        message = data.get("message", "")
                    except json.JSONDecodeError:
                        print(f"Hibás JSON: {line.strip()}")
                        continue

                    if event == "BUTTON_PRESSED":
                        print(">>> Gomb megnyomva az Androidon!")
                        with self.gps_lock:
                            self.my_gps_data.comment = message
                            self.my_gps_data.store_gps_data = True
                        self.save_queue.put(True)

                    else:
                        print(f"Üzenet: {message}")
