from RatS.base.base_ratings_uploader import RatingsUploader
from RatS.tmdb.tmdb_site import TMDB


class TMDBRatingsInserter(RatingsUploader):
    def __init__(self, args):
        super(TMDBRatingsInserter, self).__init__(TMDB(args), args)
        self.url_for_csv_file_upload = self._get_url_for_csv_upload()
        self.css_id_of_file_input_element = "csv_file"
        self.xpath_selector_for_submit_button = (
            "//form[@name='import_csv']//input[@type='submit']"
        )

    @staticmethod
    def _get_url_for_csv_upload():
        return "https://www.themoviedb.org/settings/import-list"
