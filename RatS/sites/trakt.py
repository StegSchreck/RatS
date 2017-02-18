from RatS.sites.base_site import Site


class Trakt(Site):
    def __init__(self):
        super(Trakt, self).__init__()
        self.LOGIN_PAGE = 'https://trakt.tv/auth/signin'
        self.MY_RATINGS_URL = 'https://trakt.tv/users/%s/ratings/movies/all/added' % self.USERNAME

    def login(self, browser):
        browser.get(self.LOGIN_PAGE)

        self._insert_login_credentials(browser)
        self._click_login_button(browser)

    def _insert_login_credentials(self, browser):
        login_field_user = browser.find_element_by_xpath("//form[@id='new_user']//input[@id='user_login']")
        login_field_user.send_keys(self.USERNAME)
        login_field_password = browser.find_element_by_xpath("//form[@id='new_user']//input[@id='user_password']")
        login_field_password.send_keys(self.PASSWORD)

    @staticmethod
    def _click_login_button(browser):
        login_button = browser.find_element_by_xpath("//form[@id='new_user']//input[@type='submit']")
        login_button.click()
