import datetime
import logging
import os
import time

from progressbar import ProgressBar
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementNotInteractableException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions, ui
from selenium.webdriver.support.wait import WebDriverWait

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.base.movie_entity import Movie, Site
from RatS.letterboxd.letterboxd_site import Letterboxd
from RatS.utils.file_impex import save_movies_to_csv

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S")
CSV_FILE_NAME = TIMESTAMP + "_converted_for_Letterboxd.csv"


class LetterboxdRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(LetterboxdRatingsInserter, self).__init__(Letterboxd(args), args)
        self.progress_counter_selector = ".import-progress #import-count strong"

    def insert(self, movies: list[Movie], source: Site):
        logging.info(f"===== {self.site.site_name}: posting {len(movies)} movies")

        save_movies_to_csv(
            movies,
            folder=self.exports_folder,
            filename=CSV_FILE_NAME,
            rating_source=source,
        )
        self.upload_csv_file(len(movies))

        logging.info(
            f"===== {self.site.site_name}: The file with {len(movies)} movies was uploaded "
            "and successfully processed by the servers. "
            f"You may check your {self.site.site_name} account later."
        )

        self.site.browser_handler.kill()

    def upload_csv_file(self, movies_count: int):
        self.site.browser.get("https://letterboxd.com/import/")
        time.sleep(1)
        filename = os.path.join(self.exports_folder, CSV_FILE_NAME)
        self._fill_filename_into_upload_form(filename)

        wait = ui.WebDriverWait(self.site.browser, 600)
        self._wait_for_movie_matching(wait, movies_count)
        self._wait_for_import_processing(wait, movies_count)

    def _fill_filename_into_upload_form(self, filename):
        iteration = 0
        while True:
            iteration += 1
            try:
                self.site.browser.execute_script(
                    "document.getElementById('imdb-form').setAttribute('style', 'visibility: visible;')"
                )
                self.site.browser.find_element(By.ID, "upload-imdb-import").clear()
                self.site.browser.find_element(By.ID, "upload-imdb-import").send_keys(os.path.join(filename))
                break
            except (NoSuchElementException, ElementNotInteractableException) as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue

    def _wait_for_movie_matching(self, wait, movies_count):
        logging.info(f"===== {self.site.site_name}: matching the movies...")
        # disabled_import_button_selector = "//div[@class='import-buttons']//a[@data-track-category='Import'
        # and contains(@class, 'import-button-disabled')]"
        enabled_import_button_selector = (
            "//div[@class='import-buttons']//a[@data-track-category='Import' "
            "and not(contains(@class, 'import-button-disabled'))]"
        )

        # wait.until(
        #     lambda driver: driver.find_element(
        #         By.XPATH, disabled_import_button_selector
        #     )
        # )

        self._print_progress(movies_count)

        wait.until(lambda driver: driver.find_element(By.XPATH, enabled_import_button_selector))
        self.site.browser.find_element(By.XPATH, enabled_import_button_selector).click()

    def _wait_for_import_processing(self, wait, movies_count):
        time.sleep(5)

        wait.until(lambda driver: driver.find_element(By.ID, "import-count"))
        logging.info(f"===== {self.site.site_name}: processing the movies...")

        self._print_progress(movies_count)

        WebDriverWait(self.site.browser, 600).until(
            expected_conditions.invisibility_of_element_located((By.ID, "import-count"))
        )

    def _print_progress(self, movies_count):
        if not self.progress_bar:
            self.progress_bar = ProgressBar(max_value=movies_count, redirect_stdout=True)
        while len(self.site.browser.find_elements(By.CSS_SELECTOR, self.progress_counter_selector)) != 0:
            try:
                displayed_counter = self.site.browser.find_element(By.CSS_SELECTOR, self.progress_counter_selector).text
                counter = int(displayed_counter.replace(",", "").replace(".", ""))
                self.progress_bar.update(counter)
            except (StaleElementReferenceException, NoSuchElementException):
                pass
            time.sleep(1)
        self.progress_bar.update(movies_count)
        self.progress_bar.finish()
