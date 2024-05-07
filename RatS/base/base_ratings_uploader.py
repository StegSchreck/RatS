import logging
import time

import datetime
import os

from selenium.webdriver.common.by import By

from RatS.base.base_exceptions import NoMoviesForInsertion
from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.base.base_site import BaseSite
from RatS.base.movie_entity import Site, Movie
from RatS.utils.file_impex import save_movies_to_csv

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S")


class RatingsUploader(RatingsInserter):
    def __init__(self, site: BaseSite, args):
        super(RatingsUploader, self).__init__(site, args)
        self.csv_filename = f"{TIMESTAMP}_converted_for_{site.site_name}.csv"

    def insert(self, movies: list[Movie], source: Site):
        logging.info(f"===== {self.site.site_name}: posting {len(movies)} movies")

        if self.site.site == Site.MOVIELENS:
            movies: list[Movie] = [movie for movie in movies if Site.IMDB in movie.site_data]

        if len(movies) == 0:
            self.site.browser_handler.kill()
            raise NoMoviesForInsertion(
                "There are no movies with an IMDB id in the parsed data. "
                "As the target site is looking for this id to match the data, "
                "there is nothing left to do. "
                "A workaround would be to upload the data to a third site, "
                "which knows the IMDB id, and parse again from there."
            )

        save_movies_to_csv(
            movies,
            folder=self.exports_folder,
            filename=self.csv_filename,
            rating_source=source,
        )
        self.pre_upload_action()
        self.upload_csv_file()
        self.post_upload_action()

        logging.info(
            f"===== {self.site.site_name}: The file with {len(movies)} movies was uploaded "
            "and will be process by the servers. "
            f"You may check your {self.site.site_name} account later. "
            "Note, that this might not overwrite any existing ratings."
        )

        self.site.browser_handler.kill()

    def pre_upload_action(self):
        pass

    def post_upload_action(self):
        pass

    def upload_csv_file(self):
        self.site.browser.get(self.url_for_csv_file_upload)
        time.sleep(1)
        filename = os.path.join(self.exports_folder, self.csv_filename)
        self.site.browser.find_element(By.ID, self.css_id_of_file_input_element).send_keys(filename)
        time.sleep(1)
        self.site.browser.find_element(By.XPATH, self.xpath_selector_for_submit_button).click()
        time.sleep(3)
