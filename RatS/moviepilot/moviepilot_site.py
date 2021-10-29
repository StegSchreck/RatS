import time

from selenium.webdriver.common.by import By
from RatS.base.base_site import BaseSite


class MoviePilot(BaseSite):
    def __init__(self, args):
        login_form_selector = "//*[@data-hypernova-key='LoginModule']//form"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@name='username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@name='password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        super(MoviePilot, self).__init__(args)
        self.MY_RATINGS_URL = (
            f"https://www.moviepilot.de/users/{self.USERNAME}/rated/movies"
        )

    def _get_login_page_url(self):
        return "https://www.moviepilot.de/login"

    def _handle_cookie_notice_if_present(self):
        cookie_notice_agree_buttons = self.browser.find_elements(
            By.ID, "didomi-notice-agree-button"
        )
        if len(cookie_notice_agree_buttons) == 0:
            return
        cookie_notice_agree_button = cookie_notice_agree_buttons[0]
        if cookie_notice_agree_button is not None:
            cookie_notice_agree_button.click()
            time.sleep(1)
