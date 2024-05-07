import time

from selenium.webdriver.common.by import By
from RatS.base.base_site import BaseSite


class Letterboxd(BaseSite):
    def __init__(self, args):
        login_form_selector = "//form[@id='signin-form']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='signin-username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='signin-password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"
        super(Letterboxd, self).__init__(args)
        self.MY_RATINGS_URL = f"https://letterboxd.com/{self.USERNAME}/films/ratings/"

    def _get_login_page_url(self):
        return "https://letterboxd.com/sign-in/"

    def _pre_login_action(self):
        time.sleep(2)
        video_elements = self.browser.find_elements(By.ID, "tyche_trendi_video_container")
        if len(video_elements) == 0:
            return
        video_element = video_elements[0]
        if video_element is not None:
            close_video_buttons = video_element.find_elements(By.ID, "pw-close-btn")
            if close_video_buttons is not None and len(close_video_buttons) > 0:
                close_video_buttons[0].click()
                time.sleep(1)

    def _handle_cookie_notice_if_present(self):
        cookie_notices = self.browser.find_elements(By.ID, "tyche_cmp_modal")
        if len(cookie_notices) == 0:
            return
        cookie_notice = cookie_notices[0]
        if cookie_notice is not None:
            cookie_accept_buttons = cookie_notice.find_elements(By.XPATH, "//*[contains(text(), 'Continue to Site')]")
            if cookie_accept_buttons is not None and len(cookie_accept_buttons) > 0:
                cookie_accept_buttons[0].click()
                time.sleep(1)
