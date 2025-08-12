COMMAND = "ping"


def handle_command(message: str) -> str:
    """Handle PING command by returning PONG.

    Args:
        message: The message to return PONG to

    Returns:
        PONG response
    """
    return b"+PONG\r\n"