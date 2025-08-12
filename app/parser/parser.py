def parse(self, data: bytes) -> list[bytes | None]:
    """
    Turn a chunk of RESP bytes into a list of command parts (e.g., ["SET", "foo", "bar"]).
    RESP command look like: *3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n
    """
    if not data:
        return []
    lines = data.split(b"\r\n")
    self._check_not_empty(lines)

    lines = [line for line in lines if line]
    num_parts = self._parse_array_header(lines[0])
    command = []
    current_line = 1  # Start after *n

    for _ in range(num_parts):
        if current_line >= len(lines):
            raise ValueError("Ran out of lines before finishing the command")
        part_length = self._parse_bulk_string_length(lines[current_line])
        current_line += 1

        if part_length == -1:
            command.append(None)  # Null bulk string, no data line
        else:
            if current_line >= len(lines):
                raise ValueError("Missing the data after the length line")
            command.append(
                self._parse_bulk_string(lines[current_line], part_length)
            )
            current_line += 1

    return command