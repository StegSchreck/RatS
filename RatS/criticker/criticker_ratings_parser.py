import datetime
import os
import re
import sys
import time
from xml.etree import ElementTree

from selenium.common.exceptions import TimeoutException

from RatS.base.base_ratings_parser import Parser
from RatS.criticker.criticker_site import Criticker
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')


class CritickerRatingsParser(Parser):
    def __init__(self, args):
        super(CritickerRatingsParser, self).__init__(Criticker(args), args)
        self.exports_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'RatS', 'exports'))
        self.xml_filename = '%s_%s.xml' % (TIMESTAMP, 'Criticker')

    def _parse_ratings(self):
        self._get_ratings_xml()
        with open(os.path.join(self.exports_folder, self.xml_filename), 'w+') as output_file:
            output_file.write(self.site.browser.page_source)
        self.movies = self._parse_xml()

    def _get_ratings_xml(self):
        sys.stdout.write('\r===== %s: Retrieving ratings XML' % self.site.site_name)
        sys.stdout.flush()
        time.sleep(1)
        try:
            self.site.browser.get('https://www.criticker.com/resource/rankings/conv.php?type=xml')
        except TimeoutException:
            time.sleep(1)

    def _parse_xml(self):
        file_impex.wait_for_file_to_exist(os.path.join(self.exports_folder, self.xml_filename))
        xml_data = ElementTree.parse(os.path.join(self.exports_folder, self.xml_filename)).getroot()
        return [self.convert_xml_node_to_movie(xml_node) for xml_node in xml_data.findall('film')]

    @staticmethod
    def convert_xml_node_to_movie(xml_node):
        film_header = xml_node.find('filmname').text

        movie = dict()
        movie['year'] = int(re.findall(r'\((\d{4})\)', film_header)[0])
        movie['title'] = film_header.replace('(%i)' % movie['year'], '').strip()

        movie['criticker'] = dict()
        movie['criticker']['id'] = xml_node.find('filmid').text
        movie_link = xml_node.find('filmlink').text

        movie_link = re.sub('/rating/.*', '', movie_link)

        movie['criticker']['url'] = movie_link
        movie['criticker']['my_rating'] = round(float(xml_node.find('score').text) / 10)

        movie['imdb'] = dict()
        movie['imdb']['id'] = xml_node.find('imdbid').text
        movie['imdb']['url'] = 'http://www.imdb.com/title/%s' % movie['imdb']['id']

        return movie
