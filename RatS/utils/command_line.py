import sys

from RatS.utils.bash_color import BashColor


def info(message):
    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        sys.stdout.write(f"{BashColor.OKBLUE}{message}{BashColor.END}\r\n")
    else:
        sys.stdout.write(message + "\r\n")
    sys.stdout.flush()


def warn(message):
    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        sys.stdout.write(f"{BashColor.WARNING}{message}{BashColor.END}\r\n")
    else:
        sys.stdout.write(message + "\r\n")
    sys.stdout.flush()


def error(message):
    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        sys.stderr.write(
            f"\r\n{BashColor.BOLD}{BashColor.FAIL}ERROR: {BashColor.END}"
            f"{BashColor.FAIL}{message}{BashColor.END}\r\n"
        )
    else:
        sys.stderr.write(f"\r\nERROR: {message}\r\n")
    sys.stdout.write("\r\n===== ABORTING =====\r\n")
    sys.stdout.flush()
