import csv
import datetime
import os
import sys
import time

from selenium.common.exceptions import TimeoutException

from RatS.base.base_ratings_parser import RatingsParser
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')


class RatingsDownloader(RatingsParser):
    def __init__(self, site, args):
        super(RatingsDownloader, self).__init__(site, args)
        self.csv_filename = '%s_%s.csv' % (TIMESTAMP, site.site_name)

    def _parse_ratings(self):
        self._download_ratings_csv()
        self._rename_csv_file(self.downloaded_file_name)
        self.movies = self._parse_movies_from_csv(os.path.join(self.exports_folder, self.csv_filename))

    def _download_ratings_csv(self):
        sys.stdout.write('\r===== %s: Retrieving ratings CSV file' % self.site.site_displayname)
        sys.stdout.flush()
        self.site.browser.set_page_load_timeout(10)
        time.sleep(1)

        iteration = 0
        while not self._file_was_downloaded():
            try:
                self._call_download_url()
            except TimeoutException as e:
                iteration += 1
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue

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
            sys.stdout.write('\r===== %s: CSV downloaded to %s/%s\r\n' %
                             (self.site.site_displayname, self.exports_folder, self.csv_filename))
            sys.stdout.flush()
        except FileNotFoundError:
            sys.stdout.write('\r===== %s: Could not retrieve ratings CSV\r\n' % self.site.site_displayname)
            sys.stdout.flush()

    def _parse_movies_from_csv(self, filepath):
        sys.stdout.write('===== getting movies from CSV\r\n')
        sys.stdout.flush()
        file_impex.wait_for_file_to_exist(filepath)
        with open(filepath, newline='', encoding='UTF-8') as input_file:
            reader = csv.reader(input_file, delimiter=',')
            next(reader, None)  # ignore csv header
            return [self._convert_csv_row_to_movie(row) for row in reader]

    def _convert_csv_row_to_movie(self, row):
        raise NotImplementedError("This is not the implementation you are looking for.")
