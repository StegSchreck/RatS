import os
import sys

from RatS.utils.bash_color import BashColor


def print_progress_bar(iteration, total, prefix='', suffix=''):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    _, tty_columns = get_command_line_dimensions()
    length_of_percentage_output = 12

    if iteration == total:
        progress_factor = 1
    else:
        progress_factor = iteration / float(total)

    bar_length = int(tty_columns) - len(prefix) - len(suffix) - length_of_percentage_output
    percents = "{0:.1f}".format(100 * progress_factor)
    filled_length = int(round(bar_length * progress_factor))
    filled_bar = '#' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s [%s] %s%% %s' % (prefix, filled_bar, percents, suffix))

    if progress_factor == 1:
        sys.stdout.write('\n')
    sys.stdout.flush()


def get_command_line_dimensions():
    return os.popen('stty size', 'r').read().split()


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
