import time

from RatS.base.base_site import Site


class Trakt(Site):
    def __init__(self, args):
        login_form_selector = "//form[@id='new_user']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='user_login']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='user_password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"
        super(Trakt, self).__init__(args)
        self._handle_privacy_notice_if_present()
        self.MY_RATINGS_URL = 'https://trakt.tv/users/{username}/ratings/movies/all/added'.format(
            username=self.USERNAME
        )

    def _handle_privacy_notice_if_present(self):
        privacy_notice = self.browser.find_element_by_id('sncmp-container')
        if privacy_notice is not None:
            privacy_accept_button = privacy_notice.find_elements_by_id('sncmp-popup-ok-button')
            if privacy_accept_button is not None and len(privacy_accept_button) > 0:
                privacy_accept_button[0].click()
                time.sleep(1)

    def _get_login_page_url(self):
        return "https://trakt.tv/auth/signin"
