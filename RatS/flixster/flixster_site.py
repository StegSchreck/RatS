from RatS.base.base_site import Site
from selenium.webdriver.common.by import By


class Flixster(Site):
    def __init__(self, args):
        login_form_selector = "//form[@name='login']"
        self.LOGIN_USERNAME_SELECTOR = (
            login_form_selector + "//input[@name='authLogin']"
        )
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@name='authPass']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        super(Flixster, self).__init__(args)

        if not self.CREDENTIALS_VALID:
            return

        self.MY_RATINGS_URL = (
            "https://www.flixster.com/user/current/ratings/markup/?pagesize=100"
        )
        account_link = (
            self.browser.find_element(By.ID, "profileDropdown")
            .find_element(By.TAG_NAME, "a")
            .get_attribute("href")
        )
        self.USERID = int(account_link.replace("https://www.flixster.com/user/", ""))

    def _get_login_page_url(self):
        return "https://www.flixster.com/login/"
