import os
import time

import datetime

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')


class Inserter:
    def __init__(self, site):
        self.site = site
        self.failed_movies = []
        self.exports_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'RatS', 'exports'))
        self.failed_movies_filename = '%s_%s_failed.json' % (TIMESTAMP, self.site.site_name)

    def insert(self, movies, source):
        raise NotImplementedError("Should have implemented this")
