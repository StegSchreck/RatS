import csv
import datetime
import os
import sys
import time

from selenium.common.exceptions import TimeoutException

from RatS.parsers.base_parser import Parser
from RatS.sites.imdb_site import IMDB
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'RatS', 'exports'))
CSV_FILENAME = TIMESTAMP + '_imdb.csv'


class IMDBRatingsParser(Parser):
    def __init__(self):
        super(IMDBRatingsParser, self).__init__(IMDB())

    def parse(self):
        self._parse_ratings()
        self.site.kill_browser()
        return self.movies

    def _parse_ratings(self):
        self._download_ratings_csv()
        self._rename_csv_file()
        self.movies = file_impex.load_movies_from_csv(os.path.join(EXPORTS_FOLDER, CSV_FILENAME))

    def _download_ratings_csv(self):
        sys.stdout.write('\r===== %s: Retrieving ratings CSV file' % type(self.site).__name__)
        sys.stdout.flush()
        self.site.browser.set_page_load_timeout(2)
        time.sleep(1)
        try:
            self.site.browser.get('http://www.imdb.com/list/export?list_id=ratings&author_id=%s' % self.site.USERID)
        except TimeoutException:
            time.sleep(1)

    def _rename_csv_file(self):
        filepath = os.path.join(EXPORTS_FOLDER, 'ratings.csv')
        file_impex.wait_for_file_to_exist(filepath)

        try:
            os.rename(filepath, os.path.join(EXPORTS_FOLDER, CSV_FILENAME))
            sys.stdout.write('\r===== %s: CSV downloaded to %s/%s\r\n' %
                             (type(self.site).__name__, EXPORTS_FOLDER, CSV_FILENAME))
            sys.stdout.flush()
        except FileNotFoundError:
            sys.stdout.write('\r===== %s: Could not retrieve ratings CSV\r\n' % type(self.site).__name__)
            sys.stdout.flush()
