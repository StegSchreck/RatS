import csv
import os
import re
import sys

from RatS.base.base_ratings_downloader import RatingsDownloader
from RatS.movielens.movielens_site import Movielens
from RatS.utils import file_impex


class MovielensRatingsParser(RatingsDownloader):
    def __init__(self, args):
        super(MovielensRatingsParser, self).__init__(Movielens(args), args)

    def _parse_ratings(self):
        self._download_ratings_csv()
        self._rename_csv_file('movielens-ratings.csv')
        self.movies = self._parse_movies_from_csv(os.path.join(self.exports_folder, self.csv_filename))

    def _call_download_url(self):
        self.site.browser.get('https://movielens.org/api/users/me/movielens-ratings.csv')

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

        if self.args and self.args.verbose and self.args.verbose >= 1:
            sys.stdout.write('\r===== %s: reading movie from CSV: \r\n' % self.site.site_displayname)
            for r in row:
                sys.stdout.write(r + '\r\n')
            sys.stdout.flush()

        year = self.__extract_year(movie, row)
        movie['title'] = row[5].replace(year, '').strip()

        movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['id'] = row[0]
        movie[self.site.site_name.lower()]['url'] = 'https://movielens.org/movies/' + row[0]
        movie[self.site.site_name.lower()]['my_rating'] = int(float(row[3]) * 2)

        self.__extract_imdb_informations(movie, row)
        self.__extract_tmdb_informations(movie, row)

        return movie

    @staticmethod
    def __extract_tmdb_informations(movie, row):
        movie['tmdb'] = dict()
        movie['tmdb']['id'] = row[2]
        movie['tmdb']['url'] = 'https://www.themoviedb.org/movie/' + movie['tmdb']['id']

    @staticmethod
    def __extract_imdb_informations(movie, row):
        movie['imdb'] = dict()
        movie['imdb']['id'] = row[1]
        if 'tt' not in movie['imdb']['id']:
            movie['imdb']['id'] = 'tt' + row[1]
        movie['imdb']['url'] = 'http://www.imdb.com/title/' + movie['imdb']['id']

    @staticmethod
    def __extract_year(movie, row):
        find_year = re.findall(r'(\(\d{4}\))', row[5])
        if find_year:
            year = find_year[-1]
            movie['year'] = int(re.findall(r'\((\d{4})\)', row[5])[-1])
        else:  # no movie year in CSV
            year = '()'
            movie['year'] = 0
        return year
