import sys

from RatS.base.base_ratings_parser import RatingsParser
from RatS.rottentomatoes.rottentomatoes_site import RottenTomatoes


class RottenTomatoesRatingsParser(RatingsParser):
    def __init__(self, args):
        super(RottenTomatoesRatingsParser, self).__init__(RottenTomatoes(args), args)

    def _get_ratings_page(self, i):
        return '{url}?endCursor={page_end_cursor}'.format(url=self.site.MY_RATINGS_URL, page_end_cursor=i)

    def _parse_ratings(self):
        json_data = self.site.get_json_from_html()
        sys.stdout.write('\r===== {site_displayname}: Parsing all pages with movie ratings.\r\n'.format(
                             site_displayname=self.site.site_displayname,
                         ))
        sys.stdout.flush()

        self._parse_ratings_json(json_data['ratings'])
        has_next_page = json_data['pageInfo']['hasNextPage']
        while has_next_page:
            end_cursor = json_data['pageInfo']['endCursor']
            self.site.browser.get(self._get_ratings_page(end_cursor))
            json_data = self.site.get_json_from_html()
            self._parse_ratings_json(json_data['ratings'])
            has_next_page = json_data['pageInfo']['hasNextPage']

    def _parse_ratings_json(self, ratings_json):
        for movie_json in ratings_json:
            movie = self._parse_movie_json(movie_json)
            if movie:
                self.movies.append(movie)
                self.print_progress(movie)

    def print_progress(self, movie):
        if self.args and self.args.verbose and self.args.verbose >= 2:
            sys.stdout.write(
                '\r===== {site_displayname}: [{movie_index}] '
                'parsed {movie} \r\n'.format(
                    site_displayname=self.site.site_displayname,
                    movie=movie,
                    movie_index=len(self.movies)
                ))
            sys.stdout.flush()
        elif self.args and self.args.verbose and self.args.verbose >= 1:
            sys.stdout.write(
                '\r===== {site_displayname}: [{movie_index}] '
                'parsed {movie_title} ({movie_year}) \r\n'.format(
                    site_displayname=self.site.site_displayname,
                    movie_title=movie['title'],
                    movie_year=movie['year'],
                    movie_index=len(self.movies)
                ))
            sys.stdout.flush()
        else:
            sys.stdout.write(
                '\r      Parsed {movies_count} movies so far...'.format(
                    movies_count=len(self.movies)
                ))
            sys.stdout.flush()

    @staticmethod
    def _parse_movie_json(movie_json):
        if not movie_json['review']['score']:
            return None

        movie = dict()
        movie['title'] = movie_json['item']['title']
        movie['year'] = int(movie_json['item']['releaseYear'])

        movie['rottentomatoes'] = dict()
        movie['rottentomatoes']['id'] = movie_json['item']['rtId']
        movie['rottentomatoes']['url'] = movie_json['item']['vanityUrl'].replace('http://', 'https://')
        movie['rottentomatoes']['my_rating'] = int(float(movie_json['review']['score']) * 2)

        return movie
