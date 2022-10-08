import os

from selenium.webdriver.common.by import By

from RatS.base.base_ratings_downloader import RatingsDownloader
from RatS.imdb.imdb_site import IMDB
from RatS.utils import file_impex


class IMDBRatingsParser(RatingsDownloader):
    def __init__(self, args):
        super(IMDBRatingsParser, self).__init__(IMDB(args), args)
        self.USERID = self._get_user_id()
        self.downloaded_file_name = "ratings.csv"

    def _get_user_id(self):
        self.site.browser.get("https://www.imdb.com/profile")
        return self.site.browser.find_elements(By.XPATH, "//div[@data-userid]")[
            0
        ].get_attribute("data-userid")

    def _parse_ratings(self):
        self._download_ratings_csv()
        self._rename_csv_file(self.downloaded_file_name)
        self.movies = file_impex.load_movies_from_csv(
            os.path.join(self.exports_folder, self.csv_filename), encoding="ISO-8859-1"
        )

    def _call_download_url(self):
        self.site.browser.get(
            f"https://www.imdb.com/list/export?list_id=ratings&author_id={self.USERID}"
        )
