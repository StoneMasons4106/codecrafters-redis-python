BUF_SIZE = 4096
SEPARATOR = b"\r\n"


def word(buf, pos):
    if len(buf) < pos:
        return None

    end = buf[pos:].find(b"\r")
    if end + 1 < len(buf):
        return (pos + end + 2, buf[pos : pos + end])
    return None


def simple_string(buf, pos):
    string_word = word(buf, pos)
    if string_word:
        # TODO add byte to str conversion?
        return (string_word[0], string_word[1].decode())
    return None


def integer(buf, pos):
    int_word = word(buf, pos)
    if int_word:
        # TODO add byte to int conversion
        return (int_word[0], int(int_word[1].decode()))
    return None


def bulk_string(buf, pos):
    bulk_string_len = integer(buf, pos)
    if bulk_string_len:
        (pos_next, size) = bulk_string_len
        if size == -1:
            return (pos_next, b"")
        if size >= 0:
            total_size = pos_next + size
            if len(buf) < total_size + 2:
                return None
            bulk_s = buf[pos_next:total_size]
            return (total_size + 2, bulk_s.decode())
    return None


def parse(buf, pos):
    if len(buf) == 0:
        return None

    match buf[pos : pos + 1]:
        case b"+":
            return simple_string(buf, pos + 1)
        # case b'-':
        #     return error(buf, pos + 1),
        case b"$":
            return bulk_string(buf, pos + 1)
        case b":":
            return integer(buf, pos + 1)
        case b"*":
            return array(buf, pos + 1)
        case _:
            return None
            # raise Exception("unknown param")


def array(buf, pos):
    array_len = integer(buf, pos)
    if array_len is None:
        return None
    (pos, num_elements) = array_len
    if num_elements == -1:
        return (pos, [])
    if num_elements >= 0:
        values = []
        curr_pos = pos
        for _ in range(0, num_elements):
            parse_result = parse(buf, curr_pos)
            if parse_result:
                (new_pos, value) = parse_result
                curr_pos = new_pos
                values.append(value)
            else:
                return None
        return (curr_pos, values)
    return None


def en_string(value, buf):
    res = b"+" + value.encode() + b"\r\n"
    return buf + res


def en_bulk_string(value, buf):
    res = b"$" + str(len(value)).encode() + b"\r\n" + value.encode() + b"\r\n"
    return buf + res


def en_int(value, buf):
    res = b":" + str(value).encode() + b"\r\n"
    return buf + res


def en_array(value, buf):
    res = b"*" + str(len(value)).encode() + b"\r\n"
    for item in value:
        res = encode(item, res)
    return buf + res


def encode(value, buf=b""):
    match value:
        case int():
            return en_int(value, buf)
        case str():
            return en_bulk_string(value, buf)
        case list():
            return en_array(value, buf)
        case _:
            return None


def encode_simple(value, buf=b""):
    match value:
        case int():
            return en_int(value, buf)
        case str():
            return en_string(value, buf)
        case list():
            return en_array(value, buf)
        case _:
            return None


def test_parse_redis_command():
    assert parse(b"$4\r\nECHO\r\n", 0)[1] == "ECHO"
    assert parse(b":4\r\n", 0)[1] == 4
    assert parse(b"*2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n", 0)[1] == ["ECHO", "hey"]
    assert parse(b"*2\r\n$7\r\nCOMMAND\r\n$4\r\nDOCS\r\n", 0)[1] == ["COMMAND", "DOCS"]
    assert parse(b"*1\r\n$4\r\nPING\r\n", 0)[1] == ["PING"]


def test_encode_redis_command():
    assert encode("ECHO", b"") == b"$4\r\nECHO\r\n"
    assert encode(4, b"") == b":4\r\n"
    assert encode(["ECHO", "hey"], b"") == b"*2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n"
    assert (
        encode(["COMMAND", "DOCS"], b"") == b"*2\r\n$7\r\nCOMMAND\r\n$4\r\nDOCS\r\n"
    ), 0


def test_encode_simple_redis_command():
    assert encode_simple("PONG") == b"+PONG\r\n"