import sys

from RatS.base.base_ratings_parser import RatingsParser
from RatS.base.movie_entity import Movie, Site, SiteSpecificMovieData
from RatS.flixster.flixster_site import Flixster


class FlixsterRatingsParser(RatingsParser):
    def __init__(self, args):
        super(FlixsterRatingsParser, self).__init__(Flixster(args), args)

    def _get_ratings_page(self, page_number: int):
        return f"{self.site.MY_RATINGS_URL}&page={page_number}"

    def _parse_ratings(self):
        json_data = self.site.get_json_from_html()
        self.movies_count = json_data["pagination"]["totalCount"]
        pages_count = json_data["pagination"]["pageCount"]
        ratings = json_data["ratings"]

        sys.stdout.write(
            f"\r===== {self.site.site_displayname}: Parsing {pages_count} pages"
            f" with {self.movies_count} movies in total\r\n"
        )
        sys.stdout.flush()

        self._parse_ratings_json(ratings)
        for page_number in range(2, pages_count + 1):
            self.site.browser.get(self._get_ratings_page(page_number))
            json_data = self.site.get_json_from_html()
            self._parse_ratings_json(json_data["ratings"])

    def _parse_ratings_json(self, ratings_json):
        for movie_json in ratings_json:
            movie = self._parse_movie_json(movie_json)
            self.movies.append(movie)
            self.print_progress(movie)

    @staticmethod
    def _parse_movie_json(movie_json):
        movie = Movie(
            title=movie_json["movie"]["title"], year=int(movie_json["movie"]["year"])
        )

        movie.site_data[Site.FLIXSTER] = SiteSpecificMovieData(
            id=str(movie_json["movie"]["id"]),
            url=movie_json["movie"]["url"].replace("http://", "https://"),
            my_rating=int(float(movie_json["score"]) * 2),
        )

        return movie
