import logging

from RatS.base.base_ratings_parser import RatingsParser
from RatS.base.movie_entity import Movie, Site, SiteSpecificMovieData
from RatS.rottentomatoes.rottentomatoes_site import RottenTomatoes


class RottenTomatoesRatingsParser(RatingsParser):
    def __init__(self, args):
        super(RottenTomatoesRatingsParser, self).__init__(RottenTomatoes(args), args)

    def _get_ratings_page(self, page_number: int):
        return f"{self.site.MY_RATINGS_URL}?endCursor={page_number}"

    def _parse_ratings(self):
        json_data = self.site.get_json_from_html()
        logging.info(f"===== {self.site.site_name}: Parsing all pages with movie ratings.")

        self._parse_ratings_json(json_data["ratings"])
        has_next_page = json_data["pageInfo"]["hasNextPage"]
        while has_next_page:
            end_cursor = json_data["pageInfo"]["endCursor"]
            self.site.browser.get(self._get_ratings_page(end_cursor))
            json_data = self.site.get_json_from_html()
            self._parse_ratings_json(json_data["ratings"])
            has_next_page = json_data["pageInfo"]["hasNextPage"]

    def _parse_ratings_json(self, ratings_json):
        for movie_json in ratings_json:
            movie = self._parse_movie_json(movie_json)
            if movie:
                self.movies.append(movie)
                self.print_progress(movie)

    def print_progress(self, movie: Movie):
        logging.debug(f"===== {self.site.site_name}: [{len(self.movies)}] parsed {movie.title} ({movie.year})")
        logging.info(f"Parsed {len(self.movies)} movies so far...")

    @staticmethod
    def _parse_movie_json(movie_json):
        if not movie_json["review"]["score"]:
            return None

        movie = Movie(
            title=movie_json["item"]["title"],
            year=int(movie_json["item"]["releaseYear"]),
        )

        movie.site_data[Site.ROTTENTOMATOES] = SiteSpecificMovieData(
            id=movie_json["item"]["rtId"],
            url=movie_json["item"]["vanityUrl"].replace("http://", "https://"),
            my_rating=int(float(movie_json["review"]["score"]) * 2),
        )

        return movie
