import datetime
import time

import sys

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.utils.file_impex import save_movies_to_csv

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')


class RatingsUploader(RatingsInserter):
    def __init__(self, site, args):
        super(RatingsUploader, self).__init__(site, args)
        self.csv_filename = TIMESTAMP + '_converted_for_' + site.site_name + '.csv'

    def insert(self, movies, source):
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (self.site.site_displayname, len(movies)))
        sys.stdout.flush()

        save_movies_to_csv(movies, folder=self.exports_folder, filename=self.csv_filename, rating_source=source)
        self.upload_csv_file()

        sys.stdout.write('\r\n===== %s: The file with %i movies was uploaded '
                         'and will be process by the servers. '
                         'You may check your %s account later.\r\n'
                         'Note, that this might not overwrite any existing ratings.\r\n' %
                         (self.site.site_displayname, len(movies), self.site.site_name))
        sys.stdout.flush()

        self.site.kill_browser()

    def upload_csv_file(self):
        raise NotImplementedError("This is not the implementation you are looking for.")
