import sys
import time

import csv
import datetime
import os
from selenium.common.exceptions import TimeoutException

from RatS.base.base_exceptions import CSVDownloadFailedException
from RatS.base.base_ratings_parser import RatingsParser
from RatS.base.base_site import BaseSite
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S")


class RatingsDownloader(RatingsParser):
    def __init__(self, site: BaseSite, args):
        super(RatingsDownloader, self).__init__(site, args)
        self.csv_filename = f"{TIMESTAMP}_{site.site_name}.csv"
        self.csv_delimiter = ","

    def _parse_ratings(self):
        self._download_ratings_csv()
        self._rename_csv_file(self.downloaded_file_name)
        self.movies = self._parse_movies_from_csv(
            os.path.join(self.exports_folder, self.csv_filename)
        )

    def _download_ratings_csv(self):
        sys.stdout.write(
            f"\r===== {self.site.site_displayname}: Retrieving ratings CSV file"
        )
        sys.stdout.flush()
        self.site.browser.set_page_load_timeout(10)
        time.sleep(1)

        iteration = 0
        while not self._file_was_downloaded():
            iteration += 1
            try:
                self._call_download_url()
            except TimeoutException as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue
            if iteration > 10:
                self.site.browser_handler.kill()
                CSVDownloadFailedException(
                    "The CSV file containing the movies data could not be downloaded."
                )

    def _file_was_downloaded(self):
        filepath = os.path.join(self.exports_folder, self.downloaded_file_name)
        return os.path.isfile(filepath)

    def _call_download_url(self):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _rename_csv_file(self, original_filename):
        filepath = os.path.join(self.exports_folder, original_filename)
        file_impex.wait_for_file_to_exist(filepath)

        try:
            os.rename(filepath, os.path.join(self.exports_folder, self.csv_filename))
            sys.stdout.write(
                f"\r===== {self.site.site_displayname}: CSV downloaded to "
                f"{self.exports_folder}/{self.csv_filename}\r\n"
            )
            sys.stdout.flush()
        except FileNotFoundError:
            sys.stdout.write(
                f"\r===== {self.site.site_displayname}: Could not retrieve ratings CSV\r\n"
            )
            sys.stdout.flush()

    def _parse_movies_from_csv(self, filepath: str):
        sys.stdout.write("===== getting movies from CSV\r\n")
        sys.stdout.flush()
        file_impex.wait_for_file_to_exist(filepath)
        with open(filepath, newline="", encoding="UTF-8") as input_file:
            reader = csv.reader(input_file, delimiter=self.csv_delimiter)
            headers = next(reader, None)
            return [self._convert_csv_row_to_movie(headers, row) for row in reader]

    def _convert_csv_row_to_movie(self, headers, row):
        raise NotImplementedError("This is not the implementation you are looking for.")
