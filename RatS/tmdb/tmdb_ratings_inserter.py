from RatS.base.base_ratings_uploader import RatingsUploader
from RatS.tmdb.tmdb_site import TMDB


class TMDBRatingsInserter(RatingsUploader):
    def __init__(self, args):
        super(TMDBRatingsInserter, self).__init__(TMDB(args), args)
        self.url_for_csv_file_upload = 'https://www.themoviedb.org/account/StegSchreck/import'
        self.css_id_of_file_input_element = 'csv_file'
        self.xpath_selector_for_submit_button = "//form[@name='import_csv']//input[@type='submit']"
