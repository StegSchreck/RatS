import os

import sys


def print_progress(iteration, total, prefix='', suffix=''):
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
