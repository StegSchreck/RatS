import re
import sys

from RatS.base.base_ratings_downloader import RatingsDownloader
from RatS.movielens.movielens_site import Movielens


class MovielensRatingsParser(RatingsDownloader):
    def __init__(self, args):
        super(MovielensRatingsParser, self).__init__(Movielens(args), args)
        self.downloaded_file_name = 'movielens-ratings.csv'

    def _call_download_url(self):
        self.site.browser.get('https://movielens.org/api/users/me/movielens-ratings.csv')

    def _convert_csv_row_to_movie(self, headers, row):
        movie = dict()

        if self.args and self.args.verbose and self.args.verbose >= 1:
            sys.stdout.write('\r===== {site_displayname}: reading movie from CSV: \r\n'.format(
                site_displayname=self.site.site_displayname
            ))
            for r in row:
                sys.stdout.write(r + '\r\n')
            sys.stdout.flush()

        year = self.__extract_year(movie, row[headers.index("title")])
        movie['title'] = row[headers.index("title")].replace(year, '').strip()

        movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['id'] = row[headers.index("movie_id")]
        movie[self.site.site_name.lower()]['url'] = 'https://movielens.org/movies/{movie_url_path}'.format(
            movie_url_path=row[headers.index("movie_id")]
        )
        movie[self.site.site_name.lower()]['my_rating'] = int(float(row[headers.index("rating")]) * 2)

        self.__extract_imdb_information(movie, row[headers.index("imdb_id")])
        self.__extract_tmdb_information(movie, row[headers.index("tmdb_id")])

        return movie

    @staticmethod
    def __extract_tmdb_information(movie, tmdb_id):
        movie['tmdb'] = dict()
        movie['tmdb']['id'] = tmdb_id
        movie['tmdb']['url'] = 'https://www.themoviedb.org/movie/{tmdb_id}'.format(tmdb_id=movie['tmdb']['id'])

    @staticmethod
    def __extract_imdb_information(movie, imdb_id):
        movie['imdb'] = dict()
        movie['imdb']['id'] = imdb_id
        if 'tt' not in movie['imdb']['id']:
            movie['imdb']['id'] = 'tt{imdb_id_number}'.format(imdb_id_number=imdb_id)
        movie['imdb']['url'] = 'https://www.imdb.com/title/{imdb_id}'.format(imdb_id=movie['imdb']['id'])

    @staticmethod
    def __extract_year(movie, title_field):
        find_year = re.findall(r'(\(\d{4}\))', title_field)
        if find_year:
            year = find_year[-1]
            movie['year'] = int(re.findall(r'\((\d{4})\)', title_field)[-1])
        else:  # no movie year in CSV
            year = '()'
            movie['year'] = 0
        return year
