import datetime
import os
import sys
import time

from RatS.base.base_ratings_parser import RatingsParser
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')


class RatingsDownloader(RatingsParser):
    def __init__(self, site, args):
        super(RatingsDownloader, self).__init__(site, args)
        self.exports_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'RatS', 'exports'))
        self.csv_filename = '%s_%s.csv' % (TIMESTAMP, site.site_name)

    def _parse_ratings(self):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _download_ratings_csv(self):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _rename_csv_file(self, original_filename):
        filepath = os.path.join(self.exports_folder, original_filename)
        file_impex.wait_for_file_to_exist(filepath)

        try:
            os.rename(filepath, os.path.join(self.exports_folder, self.csv_filename))
            sys.stdout.write('\r===== %s: CSV downloaded to %s/%s\r\n' %
                             (self.site.site_displayname, self.exports_folder, self.csv_filename))
            sys.stdout.flush()
        except FileNotFoundError:
            sys.stdout.write('\r===== %s: Could not retrieve ratings CSV\r\n' % self.site.site_displayname)
            sys.stdout.flush()
