import datetime
import os
import sys
import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions, ui
from selenium.webdriver.support.wait import WebDriverWait

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.letterboxd.letterboxd_site import Letterboxd
from RatS.utils.command_line import print_progress_bar
from RatS.utils.file_impex import save_movies_to_csv

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
CSV_FILE_NAME = TIMESTAMP + '_converted_for_Letterboxd.csv'


class LetterboxdRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(LetterboxdRatingsInserter, self).__init__(Letterboxd(args), args)
        self.progress_counter_selector = '.import-progress #import-count strong'

    def insert(self, movies, source):
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (self.site.site_displayname, len(movies)))
        sys.stdout.flush()

        save_movies_to_csv(movies, folder=self.exports_folder, filename=CSV_FILE_NAME, rating_source=source)
        self.upload_csv_file(len(movies))

        sys.stdout.write('\r\n===== %s: The file with %i movies was uploaded '
                         'and successfully processed by the servers. '
                         'You may check your %s account later.\r\n' %
                         (self.site.site_displayname, len(movies), self.site.site_name))
        sys.stdout.flush()

        self.site.kill_browser()

    def upload_csv_file(self, movies_count):
        self.site.browser.get('https://letterboxd.com/import/')
        time.sleep(1)
        filename = os.path.join(self.exports_folder, CSV_FILE_NAME)
        self.site.browser.find_element_by_id('upload-imdb-import').send_keys(os.path.join(filename))

        wait = ui.WebDriverWait(self.site.browser, 600)
        self._wait_for_movie_matching(wait, movies_count)
        self._wait_for_import_processing(wait, movies_count)

    def _wait_for_movie_matching(self, wait, movies_count):
        time.sleep(5)
        disabled_import_button_selector = "//div[@class='import-buttons']//a[@data-track-category='Import' and contains(@class, 'import-button-disabled')]"  # pylint: disable=line-too-long
        enabled_import_button_selector = "//div[@class='import-buttons']//a[@data-track-category='Import' and not(contains(@class, 'import-button-disabled'))]"  # pylint: disable=line-too-long

        wait.until(lambda driver: driver.find_element_by_xpath(disabled_import_button_selector))
        sys.stdout.write('\r\n===== %s: matching the movies...\r\n' % self.site.site_displayname)
        sys.stdout.flush()

        self._print_progress(movies_count)

        wait.until(lambda driver: driver.find_element_by_xpath(enabled_import_button_selector))
        self.site.browser.find_element_by_xpath(enabled_import_button_selector).click()

    def _wait_for_import_processing(self, wait, movies_count):
        time.sleep(5)

        wait.until(lambda driver: driver.find_element_by_id('import-count'))
        sys.stdout.write('\r\n===== %s: processing the movies...\r\n' % self.site.site_displayname)
        sys.stdout.flush()

        self._print_progress(movies_count)

        WebDriverWait(self.site.browser, 600).until(
            expected_conditions.invisibility_of_element_located((By.ID, 'import-count'))
        )

    def _print_progress(self, movies_count):
        while len(self.site.browser.find_elements_by_css_selector(self.progress_counter_selector)) is not 0:
            try:
                counter = int(self.site.browser.find_element_by_css_selector(self.progress_counter_selector).text)
                print_progress_bar(
                    iteration=counter,
                    total=movies_count,
                    start_timestamp=self.start_timestamp,
                    prefix=self.site.site_displayname
                )
            except StaleElementReferenceException:
                pass
            time.sleep(1)
        print_progress_bar(
            iteration=movies_count,
            total=movies_count,
            start_timestamp=self.start_timestamp,
            prefix=self.site.site_displayname
        )
