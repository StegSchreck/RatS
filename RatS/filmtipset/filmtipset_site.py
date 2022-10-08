from RatS.base.base_site import Site
from selenium.webdriver.common.by import By

LOGIN_BUTTON_SELECTOR = '//span[@id="submit" and @class="loginbutton"]'


class Filmtipset(Site):
    def __init__(self, args):
        self.LOGIN_USERNAME_SELECTOR = '//input[@id="user"]'
        self.LOGIN_PASSWORD_SELECTOR = '//input[@id="pass"]'
        self.LOGIN_BUTTON_SELECTOR = LOGIN_BUTTON_SELECTOR
        super(Filmtipset, self).__init__(args)
        self.MY_RATINGS_URL = "https://www.filmtipset.se/installningar"

    def _get_login_page_url(self):
        return "https://www.filmtipset.se"

    def _pre_login_action(self):
        self.browser.find_element(By.XPATH, "//a[@id='logintoggle']").click()
