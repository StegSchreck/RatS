import os

from RatS.base.base_ratings_downloader import RatingsDownloader
from RatS.letterboxd.letterboxd_site import Letterboxd
from RatS.utils import command_line
from RatS.utils import file_impex


class LetterboxdRatingsParser(RatingsDownloader):
    def __init__(self, args):
        super(LetterboxdRatingsParser, self).__init__(Letterboxd(args), args)
        self.downloaded_file_name = 'ratings.csv'

    def _parse_ratings(self):
        self.before = os.listdir(self.exports_folder)
        self._download_ratings_csv()

        after = os.listdir(self.exports_folder)
        change = self._get_downloaded_filename(after, self.before)
        if len(change) == 1:
            archive_filename = change.pop()  # the one file that was added to the dir
            file_impex.extract_file_from_archive(
                os.path.join(self.exports_folder, archive_filename),
                self.downloaded_file_name,
                self.exports_folder
            )
            self._rename_csv_file(self.downloaded_file_name)
            self.movies = self._parse_movies_from_csv(os.path.join(self.exports_folder, self.csv_filename))
        else:
            command_line.error('Could not determine file location')

    def _file_was_downloaded(self):
        after = os.listdir(self.exports_folder)
        change = self._get_downloaded_filename(after, self.before)
        return len(change) == 1

    @staticmethod
    def _get_downloaded_filename(after, before):
        return set(after) - set(before)

    def _call_download_url(self):
        self.site.browser.get('https://letterboxd.com/data/export/')

    def _convert_csv_row_to_movie(self, row):
        movie = dict()
        movie['title'] = row[1]
        movie['year'] = int(row[2])
        movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['url'] = row[3]
        movie[self.site.site_name.lower()]['my_rating'] = int(float(row[4]) * 2)
        return movie
