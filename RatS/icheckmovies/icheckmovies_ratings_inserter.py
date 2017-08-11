import datetime
import os
import sys
import time

from selenium.webdriver.support.select import Select

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.icheckmovies.icheckmovies_site import ICheckMovies
from RatS.utils.file_impex import save_movies_to_csv

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
CSV_FILE_NAME = TIMESTAMP + '_converted_for_iCheckMovies.csv'


class ICheckMoviesRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(ICheckMoviesRatingsInserter, self).__init__(ICheckMovies(args), args)

    def insert(self, movies, source):
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (self.site.site_name, len(movies)))
        sys.stdout.flush()

        save_movies_to_csv(movies, folder=self.exports_folder, filename=CSV_FILE_NAME, rating_source=source)
        self.site.browser.get('https://www.icheckmovies.com/import/imdbvotes/')
        time.sleep(1)
        self.site.browser.find_element_by_id('importFile').send_keys(os.path.join(self.exports_folder, CSV_FILE_NAME))
        time.sleep(1)
        favorite_criterium_select = Select(self.site.browser.find_element_by_id('importFavoriteCriterium'))
        favorite_criterium_select.select_by_value(self.site.INSERT_LIKE_LOWER_BOUND)
        time.sleep(1)
        hated_criterium_select = Select(self.site.browser.find_element_by_id('importHatedCriterium'))
        hated_criterium_select.select_by_value(self.site.INSERT_DISLIKE_UPPER_BOUND)
        time.sleep(1)
        self.site.browser.find_element_by_xpath("//form//button[@type='submit'][@id='importVotes']").click()
        time.sleep(3)

        sys.stdout.write('\r\n===== %s: The file with %i movies was uploaded and will be process by the servers. '
                         'You may check your iCheckMovies account later. '
                         'Note, that this will NOT overwrite any existing ratings.\r\n' %
                         (self.site.site_name, len(movies)))
        sys.stdout.flush()

        self.site.kill_browser()
