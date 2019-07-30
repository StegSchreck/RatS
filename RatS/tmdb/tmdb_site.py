import time

from RatS.base.base_site import Site


class TMDB(Site):
    def __init__(self, args):
        login_form_selector = "//form[@name='account_login']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"
        super(TMDB, self).__init__(args)
        self.MY_RATINGS_URL = 'https://www.themoviedb.org/u/{username}/ratings/movie'.format(
            username=self.USERNAME
        )

    def _get_login_page_url(self):
        return "https://www.themoviedb.org/login"

    def _handle_cookie_notice_if_present(self):
        if len(self.browser.find_elements_by_id('cookie_notice')) == 0:
            return
        cookie_notice = self.browser.find_element_by_id('cookie_notice')
        if cookie_notice is not None:
            cookie_accept_button = cookie_notice.find_elements_by_class_name('accept')
            if cookie_accept_button is not None and len(cookie_accept_button) > 0:
                cookie_accept_button[0].click()
                time.sleep(1)
        self.browser.refresh()
