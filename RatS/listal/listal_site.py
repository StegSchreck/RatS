import sys
import time

from RatS.base.base_site import BaseSite
from RatS.utils import command_line


class Listal(BaseSite):
    def __init__(self, args):
        login_form_selector = (
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' login-popup ')]"
            "//form[contains(concat(' ', normalize-space(@class), ' '), ' login-form ')]"
        )
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@name='username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@name='password']"
        self.LOGIN_BUTTON_SELECTOR = (
            login_form_selector
            + "//button[contains(concat(' ', normalize-space(@class), ' '), ' submit ')]"
        )
        super(Listal, self).__init__(args)
        self.MY_RATINGS_URL = (
            f"https://{self.USERNAME}.listal.com/movies/all/1/?rating=1"
        )

    def login(self):
        sys.stdout.write(f"===== {self.site_displayname}: performing login")
        sys.stdout.flush()
        self.open_url_with_521_retry(self.LOGIN_PAGE)
        time.sleep(1)
        self._insert_login_credentials()
        self._click_login_button()

    def _get_login_page_url(self):
        return "https://www.listal.com/login-iframe"

    def handle_request_blocked_by_website(self):
        if "stackpath" in self.browser.page_source:
            command_line.error("The request was blocked by the website.")
            self.browser_handler.kill()
