import sys

from RatS.parsers.base_parser import Parser
from RatS.sites.flixster_site import Flixster
from RatS.utils.command_line import print_progress


class FlixsterRatingsParser(Parser):
    def __init__(self):
        super(FlixsterRatingsParser, self).__init__(Flixster())

    def _get_ratings_page(self, i):
        return '%s&page=%i' % (self.site.MY_RATINGS_URL, i)

    def _parse_ratings(self):
        json_data = self.site.get_json_from_html()
        self.movies_count = json_data['pagination']['totalCount']
        pages_count = json_data['pagination']['pageCount']
        ratings = json_data['ratings']

        sys.stdout.write('\r===== %s: Parsing %i pages with %i movies in total\r\n' %
                         (self.site.site_name, pages_count, self.movies_count))
        sys.stdout.flush()

        self._parse_ratings_json(ratings)
        for i in range(2, pages_count + 1):
            self.site.browser.get(self._get_ratings_page(i))
            json_data = self.site.get_json_from_html()
            self._parse_ratings_json(json_data['ratings'])

    def _parse_ratings_json(self, ratings_json):
        for movie_json in ratings_json:
            movie = self._parse_movie_json(movie_json)
            self.movies.append(movie)
            print_progress(len(self.movies), self.movies_count, prefix=self.site.site_name)

    @staticmethod
    def _parse_movie_json(movie_json):
        movie = dict()
        movie['title'] = movie_json['movie']['title']
        movie['year'] = int(movie_json['movie']['year'])

        movie['flixster'] = dict()
        movie['flixster']['id'] = movie_json['movie']['id']
        movie['flixster']['url'] = movie_json['movie']['url']
        movie['flixster']['my_rating'] = int(float(movie_json['score']) * 2)

        return movie
