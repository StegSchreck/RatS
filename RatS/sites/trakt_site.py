from RatS.sites.base_site import Site


class Trakt(Site):
    def __init__(self):
        super(Trakt, self).__init__()
        self.MY_RATINGS_URL = 'https://trakt.tv/users/%s/ratings/movies/all/added' % self.USERNAME

    def _insert_login_credentials(self):
        login_field_user = self.browser.find_element_by_xpath("//form[@id='new_user']//input[@id='user_login']")
        login_field_user.send_keys(self.USERNAME)
        login_field_password = self.browser.find_element_by_xpath("//form[@id='new_user']//input[@id='user_password']")
        login_field_password.send_keys(self.PASSWORD)
