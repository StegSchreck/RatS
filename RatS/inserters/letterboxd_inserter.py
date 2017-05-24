import datetime
import os
import sys
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions, ui
from selenium.webdriver.support.wait import WebDriverWait

from RatS.inserters.base_inserter import Inserter
from RatS.sites.letterboxd_site import Letterboxd
from RatS.utils.file_impex import save_movies_to_csv

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
CSV_FILE_NAME = TIMESTAMP + '_converted_for_Letterboxd.csv'


class LetterboxdRatingsInserter(Inserter):
    def __init__(self):
        super(LetterboxdRatingsInserter, self).__init__(Letterboxd())

    def insert(self, movies, source):
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (self.site.site_name, len(movies)))
        sys.stdout.flush()

        save_movies_to_csv(movies, folder=self.exports_folder, filename=CSV_FILE_NAME, rating_source=source)
        self.site.browser.get('https://letterboxd.com/import/')
        time.sleep(1)
        self.site.browser.find_element_by_id('upload-imdb-import')\
            .send_keys(os.path.join(self.exports_folder, CSV_FILE_NAME))

        wait = ui.WebDriverWait(self.site.browser, 600)
        self._wait_for_movie_matching(wait)
        self._wait_for_import_processing(wait)

        sys.stdout.write('\r\n===== %s: The file with %i movies was uploaded '
                         'and successfully processed by the servers. '
                         'You may check your %s account later.\r\n' %
                         (self.site.site_name, len(movies), self.site.site_name))
        sys.stdout.flush()

        self.site.kill_browser()

    def _wait_for_movie_matching(self, wait):
        time.sleep(5)
        disabled_import_button_selector = "//div[@class='import-buttons']//a[@data-track-category='Import' and contains(@class, 'import-button-disabled')]"  # pylint: disable=line-too-long
        enabled_import_button_selector = "//div[@class='import-buttons']//a[@data-track-category='Import' and not(contains(@class, 'import-button-disabled'))]"  # pylint: disable=line-too-long

        wait.until(lambda driver: driver.find_element_by_xpath(disabled_import_button_selector))
        wait.until(lambda driver: driver.find_element_by_xpath(enabled_import_button_selector))
        self.site.browser.find_element_by_xpath(enabled_import_button_selector).click()

    def _wait_for_import_processing(self, wait):
        time.sleep(5)
        wait.until(lambda driver: driver.find_element_by_id('import-count'))
        WebDriverWait(self.site.browser, 600).until(
            expected_conditions.invisibility_of_element_located((By.ID, 'import-count'))
        )
