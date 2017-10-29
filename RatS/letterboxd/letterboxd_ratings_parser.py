import csv
import os
import sys
import time

from selenium.common.exceptions import TimeoutException

from RatS.base.base_ratings_downloader import RatingsDownloader
from RatS.letterboxd.letterboxd_site import Letterboxd
from RatS.utils import command_line
from RatS.utils import file_impex


class LetterboxdRatingsParser(RatingsDownloader):
    def __init__(self, args):
        super(LetterboxdRatingsParser, self).__init__(Letterboxd(args), args)

    def _parse_ratings(self):
        before = os.listdir(self.exports_folder)
        self._download_ratings_csv()

        after = os.listdir(self.exports_folder)
        change = self._get_downloaded_filename(after, before)
        if len(change) == 1:
            archive_filename = change.pop()  # the one file that was added to the dir
            ratings_csv_filename = 'ratings.csv'
            file_impex.extract_file_from_archive(
                os.path.join(self.exports_folder, archive_filename),
                ratings_csv_filename,
                self.exports_folder
            )
            self._rename_csv_file('ratings.csv')
            self.movies = self._parse_movies_from_csv(os.path.join(self.exports_folder, self.csv_filename))
        else:
            command_line.error('Could not determine file location')

    @staticmethod
    def _get_downloaded_filename(after, before):
        return set(after) - set(before)

    def _download_ratings_csv(self):
        sys.stdout.write('\r===== %s: Retrieving ratings CSV file' % self.site.site_displayname)
        sys.stdout.flush()
        self.site.browser.set_page_load_timeout(5)
        time.sleep(1)
        try:
            self.site.browser.get('https://letterboxd.com/data/export/')
        except TimeoutException:
            time.sleep(1)

    def _parse_movies_from_csv(self, filepath):
        sys.stdout.write('===== getting movies from CSV\r\n')
        sys.stdout.flush()
        file_impex.wait_for_file_to_exist(filepath)
        with open(filepath, newline='') as input_file:
            reader = csv.reader(input_file, delimiter=',')
            next(reader, None)  # ignore csv header
            return [self._convert_csv_row_to_movie(row) for row in reader]

    def _convert_csv_row_to_movie(self, row):
        movie = dict()
        movie['title'] = row[1]
        movie['year'] = int(row[2])
        movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['url'] = row[3]
        movie[self.site.site_name.lower()]['my_rating'] = int(float(row[4]) * 2)
        return movie
