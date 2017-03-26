import datetime
import os
import sys
import time

from RatS.inserters.base_inserter import Inserter
from RatS.sites.tmdb_site import TMDB
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'RatS', 'exports'))
FAILED_MOVIES_FILE = TIMESTAMP + '_tmdb_failed.json'
CSV_FILE_NAME = TIMESTAMP + '.csv'


class TMDBUploader(Inserter):
    def __init__(self):
        super(TMDBUploader, self).__init__(TMDB())

    def insert(self, movies, source):
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (self.site_name, len(movies)))
        sys.stdout.flush()

        file_impex.save_movies_to_csv(movies, folder=EXPORTS_FOLDER, filename=CSV_FILE_NAME, rating_source=source)
        self.site.browser.get('https://www.themoviedb.org/account/StegSchreck/import')
        time.sleep(1)
        self.site.browser.find_element_by_id('csv_file').send_keys(os.path.join(EXPORTS_FOLDER, CSV_FILE_NAME))
        time.sleep(1)
        self.site.browser.find_element_by_xpath("//form[@name='import_csv']//input[@type='submit']").click()
        time.sleep(3)

        sys.stdout.write('\r\n===== %s: The file with %i movies was uploaded '
                         'and will be process by the servers. You may check back later.\r\n' %
                         (self.site_name, len(movies)))
        sys.stdout.flush()

        self.site.kill_browser()
