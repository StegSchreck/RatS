import os
import sys
import time

from RatS.utils.bash_color import BashColor


def print_progress_bar(iteration, total, start_timestamp, prefix='', suffix=''):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration           - Required  : current iteration (Int)
        total               - Required  : total iterations (Int)
        start_timestamp     - Required  : timestamp when the progress was started (Int)
        prefix              - Optional  : prefix string (Str)
        suffix              - Optional  : suffix string (Str)
    """
    _, tty_columns = _get_command_line_dimensions()
    length_of_percentage_output = 6
    length_of_spaces = 6

    if iteration == total:
        progress_factor = 1
    else:
        progress_factor = iteration / float(total)

    absolute_progress = str(iteration) + "/" + str(total)
    remaining_time = _estimate_remaining_time(start_timestamp, iteration, total)
    percents = '{0:.1f}%'.format(100 * progress_factor)

    bar_length = int(tty_columns) - len(prefix) - len(absolute_progress) - len(remaining_time)\
        - len(suffix) - length_of_percentage_output - length_of_spaces

    sys.stdout.write('\r{prefix} {absolute_progress} {remaining_time} {progress_bar} {percents} {suffix}'.format(
        prefix=prefix,
        absolute_progress=absolute_progress,
        remaining_time=remaining_time,
        progress_bar=_generate_progress_bar(bar_length, progress_factor),
        percents=percents,
        suffix=suffix
    ))

    if progress_factor == 1:
        sys.stdout.write('\n')
    sys.stdout.flush()


def _generate_progress_bar(bar_length, progress_factor):
    filled_length = int(round(bar_length * progress_factor))
    filled_bar = '#' * filled_length
    unfilled_bar = '-' * (bar_length - filled_length)
    return '[{}{}]'.format(filled_bar, unfilled_bar)


def _estimate_remaining_time(start_timestamp, iteration, total):
    time_so_far = time.time() - start_timestamp
    remaining_time_estimation = (time_so_far / iteration) * total
    remaining_hours = int(remaining_time_estimation // (60 * 60))
    remaining_minutes = int((remaining_time_estimation % (60 * 60)) // 60)
    remaining_seconds = int(remaining_time_estimation % 60)
    return '{}:{:02d}:{:02d}'.format(remaining_hours, remaining_minutes, remaining_seconds)


def _get_command_line_dimensions():
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
