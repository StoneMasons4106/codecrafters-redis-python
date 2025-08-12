def format_response(message: str) -> bytes:
    """Format a message as a RESP2 simple string response.

    Args:
        message: The message to format

    Returns:
        The formatted RESP2 simple string response as bytes
    """

    return f"+{message}\r\n".encode("utf-8")


def format_error(message: str) -> bytes:
    """Format a message as a RESP2 error response.

    Args:
        message: The error message to format

    Returns:
        The formatted RESP2 error response as bytes
    """

    return f"-{message}\r\n".encode("utf-8")