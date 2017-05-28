import datetime
import os
import sys
import time

from RatS.inserters.base_inserter import Inserter
from RatS.sites.movielens_site import Movielens
from RatS.utils.file_impex import save_movies_to_csv

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
CSV_FILE_NAME = TIMESTAMP + '_converted_for_Movielens.csv'


class MovielensRatingsInserter(Inserter):
    def __init__(self, args):
        super(MovielensRatingsInserter, self).__init__(Movielens(), args)

    def insert(self, movies, source):
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (self.site.site_name, len(movies)))
        sys.stdout.flush()

        save_movies_to_csv(movies, folder=self.exports_folder, filename=CSV_FILE_NAME, rating_source=source)
        self.site.browser.get('https://movielens.org/profile/settings/import-export')
        time.sleep(1)
        self.site.browser.find_element_by_id('infile').send_keys(os.path.join(self.exports_folder, CSV_FILE_NAME))
        time.sleep(1)
        self.site.browser.find_element_by_xpath("//form[@name='importForm']//button[@type='submit']").click()
        time.sleep(3)

        sys.stdout.write('\r\n===== %s: The file with %i movies was uploaded '
                         'and will be process by the servers. '
                         'You may check your Movielens account later.\r\n' %
                         (self.site.site_name, len(movies)))
        sys.stdout.flush()

        self.site.kill_browser()
