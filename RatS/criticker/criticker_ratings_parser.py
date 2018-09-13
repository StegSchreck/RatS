import datetime
import os
import re
import sys
import time
from xml.etree import ElementTree

from selenium.common.exceptions import TimeoutException

from RatS.base.base_ratings_parser import RatingsParser
from RatS.criticker.criticker_site import Criticker
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')


class CritickerRatingsParser(RatingsParser):
    def __init__(self, args):
        super(CritickerRatingsParser, self).__init__(Criticker(args), args)
        self.xml_filename = '{timestamp}_{site_name}.xml'.format(
            timestamp=TIMESTAMP,
            site_name='Criticker'
        )

    def _parse_ratings(self):
        self._get_ratings_xml()
        with open(os.path.join(self.exports_folder, self.xml_filename), 'w+') as output_file:
            output_file.write(self.site.browser.page_source)
        self.movies = self._parse_xml()

    def _get_ratings_xml(self):
        sys.stdout.write('\r===== {site_displayname}: Retrieving ratings XML'.format(
            site_displayname=self.site.site_displayname
        ))
        sys.stdout.flush()
        time.sleep(1)

        iteration = 0
        while True:
            iteration += 1
            try:
                self.site.browser.get('https://www.criticker.com/resource/ratings/conv.php?type=xml')
                break
            except TimeoutException as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue

    def _parse_xml(self):
        file_impex.wait_for_file_to_exist(os.path.join(self.exports_folder, self.xml_filename))
        xml_data = ElementTree.parse(os.path.join(self.exports_folder, self.xml_filename)).getroot()
        return [self.convert_xml_node_to_movie(xml_node) for xml_node in xml_data.findall('film')]

    @staticmethod
    def convert_xml_node_to_movie(xml_node):
        film_header = xml_node.find('filmname').text

        movie = dict()
        movie['year'] = int(re.findall(r'\((\d{4})\)', film_header)[0])
        movie['title'] = film_header.replace('({movie_year})'.format(movie_year=movie['year']), '').strip()

        movie['criticker'] = dict()
        movie['criticker']['id'] = xml_node.find('filmid').text
        movie_link = xml_node.find('filmlink').text

        movie_link = re.sub('/rating/.*', '', movie_link)

        movie['criticker']['url'] = movie_link
        movie['criticker']['my_rating'] = round(float(xml_node.find('rating').text) / 10)

        movie['imdb'] = dict()
        movie['imdb']['id'] = xml_node.find('imdbid').text
        movie['imdb']['url'] = 'http://www.imdb.com/title/{imdb_id}'.format(imdb_id=movie['imdb']['id'])

        return movie
