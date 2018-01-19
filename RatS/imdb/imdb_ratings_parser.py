import os

from RatS.base.base_ratings_downloader import RatingsDownloader
from RatS.imdb.imdb_site import IMDB
from RatS.utils import file_impex


class IMDBRatingsParser(RatingsDownloader):
    def __init__(self, args):
        super(IMDBRatingsParser, self).__init__(IMDB(args), args)
        self.downloaded_file_name = 'ratings.csv'

    def _parse_ratings(self):
        self._download_ratings_csv()
        self._rename_csv_file(self.downloaded_file_name)
        self.movies = file_impex.load_movies_from_csv(os.path.join(self.exports_folder, self.csv_filename))

    def _call_download_url(self):
        self.site.browser.get('http://www.imdb.com/list/export?list_id=ratings&author_id={user_id}'.format(
            user_id=self.site.USERID
        ))
