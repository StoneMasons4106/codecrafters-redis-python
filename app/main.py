import socket  # noqa: F401
import threading
from app.commands import ping, echo

BUF_SIZE = 4096

def handle_command(client: socket.socket):
    while chunk := client.recv(BUF_SIZE):
        if chunk == b"PING":
            response = ping.handle_command()
        elif chunk == b"ECHO" and len(chunk) > 1:
            message_text = (
                chunk[1].decode("utf-8")
                if isinstance(chunk[1], bytes)
                else chunk[1]
            )
            response = echo.handle_command(message_text)
        else:
            response = "Unknown command"
        client.sendall(response.encode("utf-8") if isinstance(response, str) else response)

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    while True:
        client_socket, client_addr = server_socket.accept()
        threading.Thread(target=handle_command, args=(client_socket,)).start()


if __name__ == "__main__":
    main()
