import time

from RatS.base.base_site import Site


class Trakt(Site):
    def __init__(self, args):
        login_form_selector = "//form[@id='new_user']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='user_login']"
        self.LOGIN_PASSWORD_SELECTOR = (
            login_form_selector + "//input[@id='user_password']"
        )
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"
        super(Trakt, self).__init__(args)
        self._handle_privacy_notice_if_present()
        self.MY_RATINGS_URL = (
            f"https://trakt.tv/users/{self.USERNAME}/ratings/movies/all/added"
        )

    def _handle_privacy_notice_if_present(self):
        privacy_notice = self.browser.find_elements_by_id("snigel-cmp-framework")
        if len(privacy_notice) == 0:
            return
        privacy_accept_button = privacy_notice[0].find_elements_by_id("accept-choices")
        if privacy_accept_button is not None and len(privacy_accept_button) > 0:
            privacy_accept_button[0].click()
            time.sleep(1)

    def _get_login_page_url(self):
        return "https://trakt.tv/auth/signin"
