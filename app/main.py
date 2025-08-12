import re
import asyncio
from .parser.parser import parse, encode, encode_simple

async def handle_connection(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"Connection from {addr}")
    while True:
        line = await reader.read(100)
        if line == b"":
            break
        parsed = parse(line, 0)
        if parsed:
            (_, res) = parsed
            command = res[0]
            if command == "COMMAND":
                # Respond with empty map for initial COMMAND request
                writer.write(b"%0\r\n")
                await writer.drain()
                continue
            if re.search("ECHO", command, flags=re.IGNORECASE):
                # reply = b"$" + str(len(value)).encode() + b"\r\n" + value + b"\r\n"
                value = res[1]
                reply = encode(value)
                writer.write(reply)
                await writer.drain()
            if re.search("PING", command, flags=re.IGNORECASE):
                reply = encode_simple("PONG")
                writer.write(reply)
                await writer.drain()
    writer.close()
    await writer.wait_closed()

async def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server = await asyncio.start_server(handle_connection, host="localhost", port=6379)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
