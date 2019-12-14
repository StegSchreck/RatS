import sys
import time

import datetime
import os

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.base.no_movies_for_insertion import NoMoviesForInsertion
from RatS.utils.file_impex import save_movies_to_csv

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')


class RatingsUploader(RatingsInserter):
    def __init__(self, site, args):
        super(RatingsUploader, self).__init__(site, args)
        self.csv_filename = TIMESTAMP + '_converted_for_' + site.site_name + '.csv'

    def insert(self, movies, source):
        sys.stdout.write('\r===== {site_displayname}: posting {movies_count} movies\r\n'.format(
            site_displayname=self.site.site_displayname,
            movies_count=len(movies)
        ))
        sys.stdout.flush()

        if self.site.site_name.lower() == 'movielens':
            movies = [movie for movie in movies if 'imdb' in movie]

        if len(movies) == 0:
            self.site.browser_handler.kill()
            raise NoMoviesForInsertion('There are no movies with an IMDB id in the parsed data. '
                                       'As the target site is looking for this id to match the data, '
                                       'there is nothing left to do. '
                                       'A workaround would be to upload the data to a third site, '
                                       'which knows the IMDB id, and parse again from there.'
                                       )

        save_movies_to_csv(movies, folder=self.exports_folder, filename=self.csv_filename, rating_source=source)
        self.pre_upload_action()
        self.upload_csv_file()
        self.post_upload_action()

        sys.stdout.write('\r\n===== {site_displayname}: The file with {movies_count} movies was uploaded '
                         'and will be process by the servers. '
                         'You may check your {site_name} account later.\r\n'
                         'Note, that this might not overwrite any existing ratings.\r\n'.format(
                             site_displayname=self.site.site_displayname,
                             movies_count=len(movies),
                             site_name=self.site.site_name
                         ))
        sys.stdout.flush()

        self.site.browser_handler.kill()

    def pre_upload_action(self):
        pass

    def post_upload_action(self):
        pass

    def upload_csv_file(self):
        self.site.browser.get(self.url_for_csv_file_upload)
        time.sleep(1)
        filename = os.path.join(self.exports_folder, self.csv_filename)
        self.site.browser.find_element_by_id(self.css_id_of_file_input_element).send_keys(filename)
        time.sleep(1)
        self.site.browser.find_element_by_xpath(self.xpath_selector_for_submit_button).click()
        time.sleep(3)
