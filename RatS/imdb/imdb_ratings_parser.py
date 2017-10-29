import os
import sys
import time

from selenium.common.exceptions import TimeoutException

from RatS.base.base_ratings_downloader import RatingsDownloader
from RatS.imdb.imdb_site import IMDB
from RatS.utils import file_impex


class IMDBRatingsParser(RatingsDownloader):
    def __init__(self, args):
        super(IMDBRatingsParser, self).__init__(IMDB(args), args)

    def _parse_ratings(self):
        self._download_ratings_csv()
        self._rename_csv_file('ratings.csv')
        self.movies = file_impex.load_movies_from_csv(os.path.join(self.exports_folder, self.csv_filename))

    def _download_ratings_csv(self):
        sys.stdout.write('\r===== %s: Retrieving ratings CSV file' % self.site.site_displayname)
        sys.stdout.flush()
        self.site.browser.set_page_load_timeout(10)
        time.sleep(1)
        try:
            self._call_download_url()
        except TimeoutException:
            time.sleep(2)
            self._call_download_url()

    def _call_download_url(self):
        self.site.browser.get('http://www.imdb.com/list/export?list_id=ratings&author_id=%s' % self.site.USERID)
