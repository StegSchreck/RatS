import datetime
import os
import re
import sys
import time
from xml.etree import ElementTree

from selenium.common.exceptions import TimeoutException

from RatS.base.base_ratings_parser import RatingsParser
from RatS.base.movie_entity import Site, Movie, SiteSpecificMovieData
from RatS.criticker.criticker_site import Criticker
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S")


class CritickerRatingsParser(RatingsParser):
    def __init__(self, args):
        super(CritickerRatingsParser, self).__init__(Criticker(args), args)
        self.xml_filename = f"{TIMESTAMP}_Criticker.xml"

    def _parse_ratings(self):
        self._get_ratings_xml()
        with open(
            os.path.join(self.exports_folder, self.xml_filename), "w+"
        ) as output_file:
            output_file.write(self.site.browser.page_source)
        self.movies = self._parse_xml()

    def _get_ratings_xml(self):
        sys.stdout.write(
            f"\r===== {self.site.site_displayname}: Retrieving ratings XML"
        )
        sys.stdout.flush()
        time.sleep(1)

        iteration = 0
        while True:
            iteration += 1
            try:
                self.site.browser.get(
                    "https://www.criticker.com/resource/ratings/conv.php?type=xml"
                )
                break
            except TimeoutException as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue

    def _parse_xml(self):
        file_impex.wait_for_file_to_exist(
            os.path.join(self.exports_folder, self.xml_filename)
        )
        xml_data = ElementTree.parse(
            os.path.join(self.exports_folder, self.xml_filename)
        ).getroot()
        return [
            self.convert_xml_node_to_movie(xml_node)
            for xml_node in xml_data.findall("film")
        ]

    @staticmethod
    def convert_xml_node_to_movie(xml_node):
        film_header = xml_node.find("filmname").text

        movie = Movie()
        movie.year = int(re.findall(r"\((\d{4})\)", film_header)[0])
        movie.title = film_header.replace(f"({movie.year})", "").strip()

        movie.site_data[Site.CRITICKER] = SiteSpecificMovieData()
        movie.site_data[Site.CRITICKER].id = xml_node.find("filmid").text
        movie_link = xml_node.find("filmlink").text

        movie_link = re.sub("/rating/.*", "", movie_link).replace("http://", "https://")

        movie.site_data[Site.CRITICKER].url = movie_link
        movie.site_data[Site.CRITICKER].my_rating = round(
            float(xml_node.find("rating").text) / 10
        )

        movie.site_data[Site.IMDB] = SiteSpecificMovieData()
        movie.site_data[Site.IMDB].id = xml_node.find("imdbid").text
        movie.site_data[
            Site.IMDB
        ].url = f"https://www.imdb.com/title/{movie['imdb']['id']}"

        return movie
