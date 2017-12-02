from RatS.base.base_ratings_uploader import RatingsUploader
from RatS.movielens.movielens_site import Movielens


class MovielensRatingsInserter(RatingsUploader):
    def __init__(self, args):
        super(MovielensRatingsInserter, self).__init__(Movielens(args), args)
        self.url_for_csv_file_upload = 'https://movielens.org/profile/settings/import-export'
        self.css_id_of_file_input_element = 'infile'
        self.xpath_selector_for_submit_button = "//form[@name='importForm']//button[@type='submit']"
