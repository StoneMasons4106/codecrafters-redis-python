import socket  # noqa: F401
import threading
from app.commands import ping, echo
from app.parser.parser import RespParser
from .resp2 import format_response, format_error
import asyncio

async def handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    parser = RespParser.parse(reader)
    addr = writer.get_extra_info("peername")
    print(f"New connection from {addr}")

    try:
        while True:
            try:
                # Parse the incoming message
                message = await parser.parse()
                print(f"Received message: {message}")

                if not message:
                    break

                # Convert command to bytes for comparison
                command = (
                    message[0].upper()
                    if isinstance(message, list) and len(message) > 0
                    else await b""
                )

                try:
                    # Process the command
                    response = None
                    if command == b"PING":
                        response = await ping.handle_command()
                    elif command == b"ECHO" and len(message) > 1:
                        # Convert message[1] to string if it's bytes
                        message_text = (
                            message[1].decode("utf-8")
                            if isinstance(message[1], bytes)
                            else message[1]
                        )
                        response = await echo.handle_command(message_text)
                    else:
                        response = await b"+Unknown command\r\n"

                    # Send the response if we have one
                    if response is not None:
                        # Format the response if it's not already bytes
                        if not isinstance(response, (bytes, bytearray)):
                            response = format_response(response)
                        writer.write(response)
                        await writer.drain()

                except Exception as e:
                    print(f"Error processing command: {e}")
                    writer.write(format_error(f"Error: {str(e)}"))
                    await writer.drain()

            except asyncio.IncompleteReadError:
                print("Client disconnected")
                break
            except ConnectionResetError:
                print("Connection reset by peer")
                break
            except Exception as e:
                print(f"Error handling connection: {e}")
                writer.write(b"-ERR internal error\r\n")
                await writer.drain()
                break

    finally:
        print(f"Closing connection from {addr}")
        writer.close()
        await writer.wait_closed()

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 6379))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while True:
        client_socket, client_addr = server_socket.accept()
        threading.Thread(target=asyncio.run, args=(handle_connection(client_socket, client_addr,))).start()


if __name__ == "__main__":
    main()
