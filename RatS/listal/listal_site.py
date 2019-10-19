from RatS.base.base_site import Site
from RatS.utils import command_line


class Listal(Site):
    def __init__(self, args):
        login_form_selector = "//*[contains(concat(' ', normalize-space(@class), ' '), ' login-popup ')]" \
                              "//form[contains(concat(' ', normalize-space(@class), ' '), ' login-form ')]"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@name='username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@name='password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + \
            "//button[contains(concat(' ', normalize-space(@class), ' '), ' submit ')]"
        super(Listal, self).__init__(args)
        self.MY_RATINGS_URL = 'http://{username}.listal.com/movies/all/1/?rating=1'.format(username=self.USERNAME)

    def _get_login_page_url(self):
        return "https://www.listal.com/login"

    def handle_request_blocked_by_website(self):
        if 'stackpath' in self.browser.page_source:
            command_line.error("The request was blocked by the website.")
            self.browser_handler.kill()
