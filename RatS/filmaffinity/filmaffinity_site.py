import time

from RatS.base.base_site import Site
from selenium.webdriver.common.by import By


class FilmAffinity(Site):
    def __init__(self, args):
        login_form_selector = "//form[@id='login-form']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@name='username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@name='password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"
        super(FilmAffinity, self).__init__(args)
        self.MY_RATINGS_URL = "https://www.filmaffinity.com/en/myvotes.php"

    def _get_login_page_url(self):
        return "https://www.filmaffinity.com/en/login.php"

    def _handle_cookie_notice_if_present(self):
        cookie_notices = self.browser.find_elements(By.ID, "qc-cmp2-container")
        if len(cookie_notices) == 0:
            return
        cookie_notice = cookie_notices[0]
        if cookie_notice is not None:
            # agree
            cookie_accept_button = cookie_notice.find_elements(
                By.CSS_SELECTOR, By.CSS_SELECTOR, "div.qc-cmp2-summary-buttons button"
            )
            if cookie_accept_button is not None and len(cookie_accept_button) > 1:
                cookie_accept_button[1].click()
                time.sleep(2)
                # agree all
                cookie_accept_button = cookie_notice.find_elements(
                    By.CSS_SELECTOR,
                    By.CSS_SELECTOR,
                    "div.qc-cmp2-buttons-desktop button",
                )
                if cookie_accept_button is not None and len(cookie_accept_button) > 1:
                    cookie_accept_button[1].click()
                    time.sleep(2)
