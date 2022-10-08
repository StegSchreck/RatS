import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from RatS.base.base_ratings_uploader import RatingsUploader
from RatS.icheckmovies.icheckmovies_site import ICheckMovies


class ICheckMoviesRatingsInserter(RatingsUploader):
    def __init__(self, args):
        super(ICheckMoviesRatingsInserter, self).__init__(ICheckMovies(args), args)
        self.url_for_csv_file_upload = "https://www.icheckmovies.com/import/imdbvotes/"
        self.css_id_of_file_input_element = "importFile"
        self.xpath_selector_for_submit_button = (
            "//form//button[@type='submit'][@id='importVotes']"
        )

    def upload_csv_file(self):
        self.site.browser.get(self.url_for_csv_file_upload)
        time.sleep(1)
        filename = os.path.join(self.exports_folder, self.csv_filename)
        self.site.browser.find_element(
            By.ID, self.css_id_of_file_input_element
        ).send_keys(filename)
        time.sleep(1)
        favorite_criterium_select = Select(
            self.site.browser.find_element(By.ID, "importFavoriteCriterium")
        )
        favorite_criterium_select.select_by_value(self.site.INSERT_LIKE_LOWER_BOUND)
        time.sleep(1)
        hated_criterium_select = Select(
            self.site.browser.find_element(By.ID, "importHatedCriterium")
        )
        hated_criterium_select.select_by_value(self.site.INSERT_DISLIKE_UPPER_BOUND)
        time.sleep(1)
        self.site.browser.find_element(
            By.XPATH, self.xpath_selector_for_submit_button
        ).click()
        time.sleep(3)
