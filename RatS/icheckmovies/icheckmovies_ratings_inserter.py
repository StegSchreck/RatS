import os
import time

from selenium.webdriver.support.select import Select

from RatS.base.base_ratings_uploader import RatingsUploader
from RatS.icheckmovies.icheckmovies_site import ICheckMovies


class ICheckMoviesRatingsInserter(RatingsUploader):
    def __init__(self, args):
        super(ICheckMoviesRatingsInserter, self).__init__(ICheckMovies(args), args)

    def upload_csv_file(self):
        self.site.browser.get('https://www.icheckmovies.com/import/imdbvotes/')
        time.sleep(1)
        filename = os.path.join(self.exports_folder, self.csv_filename)
        self.site.browser.find_element_by_id('importFile').send_keys(filename)
        time.sleep(1)
        favorite_criterium_select = Select(self.site.browser.find_element_by_id('importFavoriteCriterium'))
        favorite_criterium_select.select_by_value(self.site.INSERT_LIKE_LOWER_BOUND)
        time.sleep(1)
        hated_criterium_select = Select(self.site.browser.find_element_by_id('importHatedCriterium'))
        hated_criterium_select.select_by_value(self.site.INSERT_DISLIKE_UPPER_BOUND)
        time.sleep(1)
        self.site.browser.find_element_by_xpath("//form//button[@type='submit'][@id='importVotes']").click()
        time.sleep(3)
