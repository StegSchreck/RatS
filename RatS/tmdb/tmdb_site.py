import time

from selenium.webdriver.common.by import By
from RatS.base.base_site import BaseSite


class TMDB(BaseSite):
    def __init__(self, args):
        login_form_selector = "//form[@name='account_login']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"
        super(TMDB, self).__init__(args)
        self.MY_RATINGS_URL = f"https://www.themoviedb.org/u/{self.USERNAME}/ratings/movie"

    def _get_login_page_url(self):
        return "https://www.themoviedb.org/login"

    def _handle_cookie_notice_if_present(self):
        cookie_notices = self.browser.find_elements(By.ID, "cookie_notice")
        if len(cookie_notices) == 0:
            return
        cookie_notice = cookie_notices[0]
        if cookie_notice is not None:
            cookie_accept_button = cookie_notice.find_elements(By.CLASS_NAME, "accept")
            if cookie_accept_button is not None and len(cookie_accept_button) > 0:
                cookie_accept_button[0].click()
                time.sleep(1)
        self.browser.refresh()
