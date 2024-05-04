def escape_filename(raw_filename: str) -> str:
    """Return an escaped version of filename.

    A filename like normal.txt will be unchanged. However, filenames
    containing backslashes and newlines are escaped with extra
    backslashes.
    """

    escaped_filename = raw_filename.replace("\\", "\\\\")
    escaped_filename = escaped_filename.replace("\n", "\\n")

    return escaped_filename

def unescape_filename(escaped_filename: str) -> str:
    """Return an unescaped version of escaped_filename.

    Most normal filenames will be unchanged. However, filenames
    containing backslashses and newlines will be changed.
    """

    unescaped_filename = escaped_filename.encode("utf-8").decode("unicode_escape")

    return unescaped_filename
