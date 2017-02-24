import sys
from selenium.webdriver import PhantomJS


class Parser:
    def __init__(self, site):
        self.site = site

        self.movies = []

        self.browser = PhantomJS()
        self.site.login(self.browser)
        self.browser.get(self.site.MY_RATINGS_URL)

    def parse(self):
        raise NotImplementedError("Should have implemented this")

    def kill_browser(self):
        self.browser.stop_client()
        self.browser.close()
        self.browser.quit()

    @staticmethod
    def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
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
        str_format = "{0:." + str(decimals) + "f}"
        percents = str_format.format(100 * (iteration / float(total)))
        filled_length = int(round(bar_length * iteration / float(total)))
        bar = '#' * filled_length + '-' * (bar_length - filled_length)

        sys.stdout.write('\r%s [%s] %s%% %s' % (prefix, bar, percents, suffix)),

        if iteration == total:
            sys.stdout.write('\n')
        sys.stdout.flush()
