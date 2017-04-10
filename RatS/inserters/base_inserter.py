import datetime
import os
import sys
import time

from RatS.utils import file_impex

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

    def _print_summary(self, movies):
        success_number = len(movies) - len(self.failed_movies)
        sys.stdout.write('\r\n===== %s: sucessfully posted %i of %i movies\r\n' %
                         (self.site.site_name, success_number, len(movies)))
        sys.stdout.flush()

    def _handle_failed_movies(self, movies):
        for failed_movie in self.failed_movies:
            sys.stdout.write('FAILED TO FIND: %s (%i)\r\n' % (failed_movie['title'], failed_movie['year']))
        if len(self.failed_movies) > 0:
            file_impex.save_movies_to_json(movies, folder=self.exports_folder, filename=self.failed_movies_filename)
            sys.stdout.write('===== %s: export data for %i failed movies to %s/%s\r\n' %
                             (self.site.site_name, len(self.failed_movies),
                              self.exports_folder, self.failed_movies_filename))
        sys.stdout.flush()
