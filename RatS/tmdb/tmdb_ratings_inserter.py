import datetime
import os
import sys
import time

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.tmdb.tmdb_site import TMDB
from RatS.utils.file_impex import save_movies_to_csv

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
CSV_FILE_NAME = TIMESTAMP + '_converted_for_TMDB.csv'


class TMDBRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(TMDBRatingsInserter, self).__init__(TMDB(args), args)

    def insert(self, movies, source):
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (self.site.site_name, len(movies)))
        sys.stdout.flush()

        save_movies_to_csv(movies, folder=self.exports_folder, filename=CSV_FILE_NAME, rating_source=source)
        self.upload_csv_file()

        sys.stdout.write('\r\n===== %s: The file with %i movies was uploaded '
                         'and will be process by the servers. '
                         'You may check your %s account later. '
                         'Note, that this will NOT overwrite any existing ratings.\r\n' %
                         (self.site.site_name, len(movies), self.site.site_name))
        sys.stdout.flush()

        self.site.kill_browser()

    def upload_csv_file(self):
        self.site.browser.get('https://www.themoviedb.org/account/StegSchreck/import')
        time.sleep(1)
        self.site.browser.find_element_by_id('csv_file').send_keys(os.path.join(self.exports_folder, CSV_FILE_NAME))
        time.sleep(1)
        self.site.browser.find_element_by_xpath("//form[@name='import_csv']//input[@type='submit']").click()
        time.sleep(3)
