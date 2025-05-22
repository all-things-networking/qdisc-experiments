import socket
import time

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5001

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    start_time = time.time()
    total_data = 0

    while True:
        data = conn.recv(4096)
        if not data:
            break
        total_data += len(data)
        
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            speed_kbps = (total_data / 1024) / elapsed_time
            print(f"Session {addr}: {speed_kbps:.2f} KB/s")

    conn.close()
    print(f"Connection closed: {addr}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print(f"Listening on {PORT}...")

    while True:
        conn, addr = server.accept()
        handle_client(conn, addr)
