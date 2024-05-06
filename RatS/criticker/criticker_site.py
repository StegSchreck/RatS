import time

from selenium.webdriver.common.by import By
from RatS.base.base_site import BaseSite


class Criticker(BaseSite):
    def __init__(self, args):
        login_form_selector = "//*[@id='i_body']//form"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='si_username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='si_password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        super(Criticker, self).__init__(args)
        self.MY_RATINGS_URL = "https://www.criticker.com/rankings/"

    def _get_login_page_url(self):
        return "https://www.criticker.com/signin.php"

    def _handle_cookie_notice_if_present(self):
        cookie_notices = self.browser.find_elements(By.ID, "i_cookies")
        if len(cookie_notices) == 0:
            return
        cookie_notice = cookie_notices[0]
        if cookie_notice is not None:
            cookie_accept_buttons = cookie_notice.find_elements(By.ID, "cookieagree")
            if cookie_accept_buttons is not None and len(cookie_accept_buttons) > 0:
                cookie_accept_buttons[0].click()
                time.sleep(1)
