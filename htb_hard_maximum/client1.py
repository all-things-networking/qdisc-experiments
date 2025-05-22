import socket
import time

SERVER_IP = '10.0.3.7'  # Change to actual server IP
PORT = 5001
RATE_KBPS = 75  # Initial download speed target (KB/s)

def send_data(rate_kbps, duration=30):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((SERVER_IP, PORT))
        print(f"Connected to {SERVER_IP}:{PORT}")

        chunk_size = 1024  # 1 KB chunks
        interval = chunk_size / (rate_kbps * 1024)  # Time per chunk

        start_time = time.time()
        while time.time() - start_time < duration:
            client.sendall(b'x' * chunk_size)
            time.sleep(interval)

send_data(RATE_KBPS)

