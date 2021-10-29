import sys

from RatS.base.base_ratings_parser import RatingsParser
from RatS.rottentomatoes.rottentomatoes_site import RottenTomatoes


class RottenTomatoesRatingsParser(RatingsParser):
    def __init__(self, args):
        super(RottenTomatoesRatingsParser, self).__init__(RottenTomatoes(args), args)

    def _get_ratings_page(self, page_number):
        return f"{self.site.MY_RATINGS_URL}?endCursor={page_number}"

    def _parse_ratings(self):
        json_data = self.site.get_json_from_html()
        sys.stdout.write(
            f"\r===== {self.site.site_displayname}: Parsing all pages with movie ratings.\r\n"
        )
        sys.stdout.flush()

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

    def print_progress(self, movie):
        if self.args and self.args.verbose and self.args.verbose >= 2:
            sys.stdout.write(
                f"\r===== {self.site.site_displayname}: [{len(self.movies)}] parsed {movie} \r\n"
            )
            sys.stdout.flush()
        elif self.args and self.args.verbose and self.args.verbose >= 1:
            sys.stdout.write(
                f"\r===== {self.site.site_displayname}: [{len(self.movies)}] parsed"
                f" {movie['title']} ({movie['year']}) \r\n"
            )
            sys.stdout.flush()
        else:
            sys.stdout.write(f"\r      Parsed {len(self.movies)} movies so far...")
            sys.stdout.flush()

    @staticmethod
    def _parse_movie_json(movie_json):
        if not movie_json["review"]["score"]:
            return None

        movie = dict()
        movie["title"] = movie_json["item"]["title"]
        movie["year"] = int(movie_json["item"]["releaseYear"])

        movie["rottentomatoes"] = dict()
        movie["rottentomatoes"]["id"] = movie_json["item"]["rtId"]
        movie["rottentomatoes"]["url"] = movie_json["item"]["vanityUrl"].replace(
            "http://", "https://"
        )
        movie["rottentomatoes"]["my_rating"] = int(
            float(movie_json["review"]["score"]) * 2
        )

        return movie
