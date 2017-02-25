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
    _, tty_columns = os.popen('stty size', 'r').read().split()
    length_of_percentage_output = 12

    bar_length = int(tty_columns) - len(prefix) - len(suffix) - length_of_percentage_output
    percents = "{0:.1f}".format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    filled_bar = '#' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s [%s] %s%% %s' % (prefix, filled_bar, percents, suffix))

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()
