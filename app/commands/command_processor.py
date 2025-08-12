from functools import partial
import asyncio


async def processEcho(data_oracle, echo):
    return echo


async def processGet(data_oracle, key):
    lock = asyncio.Lock()
    async with lock:
        out = data_oracle.get(key)
    # lock released automatically
    return out


async def processSet(data_oracle, key, val):
    lock = asyncio.Lock()
    print(f"Calling set with {key} {val}")
    async with lock:
        out = data_oracle.set(key, val)
        print(data_oracle.key_map)
    return out


async def processPing():
    return "PONG"


# Take output buffer from parser and carry out any actions
# before replying with what should be sent back to client
class CommandProcessor:

    def __init__(self, data_oracle) -> None:
        self.commands = {}
        # partial of async def requries python >=3.8
        self.commands["PING"] = processPing
        self.commands["ECHO"] = partial(processEcho, data_oracle)
        self.commands["SET"] = partial(processSet, data_oracle)
        self.commands["GET"] = partial(processGet, data_oracle)
        self.data_oracle = data_oracle

    async def process(self, input):
        # input is the output buffer of the parser
        # should be either a simple string
        # PING or an array command
        if input == "PING":
            # return "+PONG\r\n"
            return "PONG"
        assert len(input) > 0
        if input[2].upper() not in self.commands:
            print("Error command not found!")
            return None
        commandfunc = self.commands[input[2].upper()]
        # unpack arguments are the function arguments
        # order matters here
        output = await commandfunc(*input[3::2])
        return output

