import fileinput
import glob
import os
import re
from shutil import copyfile

from RatS.base.base_ratings_downloader import RatingsDownloader
from RatS.filmtipset.filmtipset_site import Filmtipset


class FilmtipsetRatingsParser(RatingsDownloader):
    def __init__(self, args):
        super(FilmtipsetRatingsParser, self).__init__(Filmtipset(args), args)
        self.downloaded_file_name = ''
        self.csv_delimiter = ';'

    # TODO remove when filmtipset has cleaned up thier "csv" file
    @staticmethod
    def _repair_csv_row(row):
        output = re.search(
            r'([0-9]{4}-[0-9]{2}-[0-9]{2}),(.*)(;[\-0-9]*;[1-5])$', row)

        if output is None:
            return row
        escaped_title_value = output.group(2).replace('"', '""')
        repaired_row = '{date};"{title}"{rest}\n'.format(
            date=output.group(1),
            title=escaped_title_value,
            rest=output.group(3))
        return repaired_row

    @staticmethod
    def _repair_csv_file(filepath):
        copyfile(filepath, filepath + '.bak')
        for line in fileinput.input(filepath, inplace=True):
            print(FilmtipsetRatingsParser._repair_csv_row(line), end="")

    def _file_was_downloaded(self):
        pattern = self.exports_folder + \
            '/ft_betyg_[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9].csv'
        files = glob.glob(pattern)
        for filename in files:
            self.downloaded_file_name = os.path.basename(filename)
            return True
        return False

    def _parse_ratings(self):
        self._download_ratings_csv()
        self._rename_csv_file(self.downloaded_file_name)
        filepath = os.path.join(self.exports_folder, self.csv_filename)
        self._repair_csv_file(filepath)
        self.movies = self._parse_movies_from_csv(filepath)

    def _call_download_url(self):
        input_xpath = '//input[@id="submit-export"]'
        self.site.browser.find_element_by_xpath(input_xpath).click()

    def _convert_csv_row_to_movie(self, headers, row):
        movie = dict()
        movie['title'] = row[headers.index("MovieTitle")]
        movie[self.site.site_name.lower()] = dict()
        my_rating = int(row[headers.index("Score")])
        movie[self.site.site_name.lower()]['my_rating'] = my_rating * 2
        self._extract_imdb_informations(movie, row[headers.index("IMDB")])

        return movie

    @staticmethod
    def _extract_imdb_informations(movie, imdb_id):
        try:
            i = int(imdb_id)
            if i < 1:
                return
        except ValueError:
            return

        imdb = dict()
        imdb['id'] = 'tt{imdb_id_number:07d}'.format(
            imdb_id_number=int(imdb_id))
        imdb['url'] = 'https://www.imdb.com/title/{imdb_id}'.format(
            imdb_id=imdb['id'])

        movie['imdb'] = imdb
