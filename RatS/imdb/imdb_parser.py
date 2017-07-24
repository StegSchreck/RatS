import datetime
import os
import sys
import time

from selenium.common.exceptions import TimeoutException

from RatS.base.base_parser import Parser
from RatS.imdb.imdb_site import IMDB
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')


class IMDBRatingsParser(Parser):
    def __init__(self, args):
        super(IMDBRatingsParser, self).__init__(IMDB(args), args)
        self.exports_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'RatS', 'exports'))
        self.csv_filename = '%s_%s.csv' % (TIMESTAMP, 'IMDB')

    def _parse_ratings(self):
        self._download_ratings_csv()
        self._rename_csv_file()
        self.movies = file_impex.load_movies_from_csv(os.path.join(self.exports_folder, self.csv_filename))

    def _download_ratings_csv(self):
        sys.stdout.write('\r===== %s: Retrieving ratings CSV file' % self.site.site_name)
        sys.stdout.flush()
        self.site.browser.set_page_load_timeout(5)
        time.sleep(1)
        try:
            self.site.browser.get('http://www.imdb.com/list/export?list_id=ratings&author_id=%s' % self.site.USERID)
        except TimeoutException:
            time.sleep(1)

    def _rename_csv_file(self):
        filepath = os.path.join(self.exports_folder, 'ratings.csv')
        file_impex.wait_for_file_to_exist(filepath)

        try:
            os.rename(filepath, os.path.join(self.exports_folder, self.csv_filename))
            sys.stdout.write('\r===== %s: CSV downloaded to %s/%s\r\n' %
                             (self.site.site_name, self.exports_folder, self.csv_filename))
            sys.stdout.flush()
        except FileNotFoundError:
            sys.stdout.write('\r===== %s: Could not retrieve ratings CSV\r\n' % self.site.site_name)
            sys.stdout.flush()
