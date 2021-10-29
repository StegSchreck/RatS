import time

from selenium.webdriver.common.by import By
from RatS.base.base_site import BaseSite


class RottenTomatoes(BaseSite):
    def __init__(self, args):
        login_form_selector = "//form[@id='login-form']"
        self.LOGIN_USERNAME_SELECTOR = (
            login_form_selector + "//input[@id='login-form-username']"
        )
        self.LOGIN_PASSWORD_SELECTOR = (
            login_form_selector + "//input[@id='login-form-password']"
        )
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"
        super(RottenTomatoes, self).__init__(args)

        if not self.CREDENTIALS_VALID:
            return

        self.MY_RATINGS_URL = self._get_ratings_url()

    def _get_login_page_url(self):
        return "https://www.rottentomatoes.com/"

    def _pre_login_action(self):
        self.browser.find_element(
            By.XPATH, "//*[@id='masthead-show-login-btn']"
        ).click()
        time.sleep(1)

    def _user_is_not_logged_in(self):
        return (
            len(
                self.browser.find_elements(By.CLASS_NAME, "masthead-account__user-link")
            )
            == 0
        )

    def _get_ratings_url(self):
        time.sleep(1)  # wait for user login status to be checked
        account_link = self.browser.find_element(
            By.CLASS_NAME, "masthead-account__user-link"
        ).get_attribute("href")
        self.USERID = account_link.replace(
            "https://www.rottentomatoes.com/user/id/", ""
        ).split("/")[0]
        return f"https://www.rottentomatoes.com/napi/userProfile/movieRatings/{self.USERID}"
