import os
import time

from RatS.base.base_ratings_uploader import RatingsUploader
from RatS.tmdb.tmdb_site import TMDB


class TMDBRatingsInserter(RatingsUploader):
    def __init__(self, args):
        super(TMDBRatingsInserter, self).__init__(TMDB(args), args)

    def upload_csv_file(self):
        self.site.browser.get('https://www.themoviedb.org/account/StegSchreck/import')
        time.sleep(1)
        filename = os.path.join(self.exports_folder, self.csv_filename)
        self.site.browser.find_element_by_id('csv_file').send_keys(filename)
        time.sleep(1)
        self.site.browser.find_element_by_xpath("//form[@name='import_csv']//input[@type='submit']").click()
        time.sleep(3)
