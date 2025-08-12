import asyncio
from .commands.command_processor import CommandProcessor
from .data_oracle import DataOracle

async def handle_connection(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"Connection from {addr}")
    while True:
        line = await reader.read(4096)
        data_oracle = DataOracle()
        command_processor = CommandProcessor(data_oracle)
        if not line:
            print("No data received, closing connection.")
            break
        line = line.decode("utf-8").strip()
        if line == "QUIT":
            print("Received QUIT command, closing connection.")
            break
        input_data = line.split()
        output = await command_processor.process(input_data)
        if output is None:
            response = b"+Error: Command not found\r\n"
        else:
            response = output.encode("utf-8") + b"\r\n"
        print(f"Sending response: {response}")
        writer.write(response)
        await writer.drain()
    print("Closing connection.")
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
