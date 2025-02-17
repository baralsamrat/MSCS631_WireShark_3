# udp_server.py
import socket

def main():
    server_address = ('127.0.0.1', 9999)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(server_address)
        print(f"UDP server listening on {server_address}")
        while True:
            data, addr = sock.recvfrom(4096)
            if data:
                print(f"Received from {addr}: {data.decode()}")
                response = "Hello from server!"
                sock.sendto(response.encode(), addr)

if __name__ == "__main__":
    main()
