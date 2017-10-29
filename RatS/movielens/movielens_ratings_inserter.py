import os
import time

from RatS.base.base_ratings_uploader import RatingsUploader
from RatS.movielens.movielens_site import Movielens


class MovielensRatingsInserter(RatingsUploader):
    def __init__(self, args):
        super(MovielensRatingsInserter, self).__init__(Movielens(args), args)

    def upload_csv_file(self):
        self.site.browser.get('https://movielens.org/profile/settings/import-export')
        time.sleep(1)
        filename = os.path.join(self.exports_folder, self.csv_filename)
        self.site.browser.find_element_by_id('infile').send_keys(filename)
        time.sleep(1)
        self.site.browser.find_element_by_xpath("//form[@name='importForm']//button[@type='submit']").click()
        time.sleep(3)
