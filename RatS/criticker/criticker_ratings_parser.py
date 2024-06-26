import datetime
import logging
import os
import re
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
        with open(os.path.join(self.exports_folder, self.xml_filename), "w+") as output_file:
            output_file.write(self.site.browser.page_source)
        self.movies = self._parse_xml()

    def _get_ratings_xml(self):
        logging.info(f"===== {self.site.site_name}: Retrieving ratings XML")
        time.sleep(1)

        iteration = 0
        while True:
            iteration += 1
            try:
                self.site.browser.get("https://www.criticker.com/resource/ratings/conv.php?type=xml")
                break
            except TimeoutException as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue

    def _parse_xml(self):
        file_impex.wait_for_file_to_exist(os.path.join(self.exports_folder, self.xml_filename))
        xml_data = ElementTree.parse(os.path.join(self.exports_folder, self.xml_filename)).getroot()
        return [self.convert_xml_node_to_movie(xml_node) for xml_node in xml_data.findall("film")]

    @staticmethod
    def convert_xml_node_to_movie(xml_node):
        film_header = xml_node.find("filmname").text

        movie_year = int(re.findall(r"\((\d{4})\)", film_header)[0])
        movie_title = film_header.replace(f"({movie_year})", "").strip()
        movie = Movie(title=movie_title, year=movie_year)

        movie.site_data = dict()
        movie_link = xml_node.find("filmlink").text
        movie_link = re.sub("/rating/.*", "", movie_link).replace("http://", "https://")

        movie.site_data[Site.CRITICKER] = SiteSpecificMovieData(
            id=xml_node.find("filmid").text,
            url=movie_link,
            my_rating=round(float(xml_node.find("rating").text) / 10),
        )

        imdb_id = xml_node.find("imdbid").text
        movie.site_data[Site.IMDB] = SiteSpecificMovieData(
            id=imdb_id,
            url=f"https://www.imdb.com/title/{imdb_id}",
        )

        return movie
