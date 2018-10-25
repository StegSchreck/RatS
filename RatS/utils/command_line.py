import sys

from RatS.utils.bash_color import BashColor


def info(message):
    if sys.stdout.isatty():
        sys.stdout.write(BashColor.OKBLUE + message + BashColor.END + "\r\n")
    else:
        sys.stdout.write(message + "\r\n")
    sys.stdout.flush()


def warn(message):
    if sys.stdout.isatty():
        sys.stdout.write(BashColor.WARNING + message + BashColor.END + "\r\n")
    else:
        sys.stdout.write(message + "\r\n")
    sys.stdout.flush()


def error(message):
    if sys.stdout.isatty():
        sys.stderr.write(BashColor.BOLD + BashColor.FAIL + '\r\nERROR: ' + BashColor.END +
                         BashColor.FAIL + message + '\r\n' + BashColor.END)
    else:
        sys.stderr.write('\r\nERROR: ' + message + '\r\n')
    sys.stdout.write('\r\n===== ABORTING =====\r\n')
    sys.stdout.flush()
