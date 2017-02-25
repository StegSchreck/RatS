from RatS.sites.base_site import Site


class Movielense(Site):
    def __init__(self):
        super(Movielense, self).__init__()
        self.MY_RATINGS_URL = 'https://movielens.org/explore/your-ratings'

    def _insert_login_credentials(self, browser):
        login_field_user = browser.find_element_by_xpath("//form//input[@id='inputEmail']")
        login_field_user.send_keys(self.USERNAME)
        login_field_password = browser.find_element_by_xpath("//form//input[@id='inputPassword']")
        login_field_password.send_keys(self.PASSWORD)