import time

from RatS.base.base_site import Site


class MoviePilot(Site):
    def __init__(self, args):
        login_form_selector = "//*[@data-hypernova-key='LoginModule']//form"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@name='username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@name='password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        super(MoviePilot, self).__init__(args)
        self.MY_RATINGS_URL = 'https://www.moviepilot.de/users/{username}/rated/movies'.format(
            username=self.USERNAME
        )

    def _get_login_page_url(self):
        return "https://www.moviepilot.de/login"

    def _handle_cookie_notice_if_present(self):
        cookie_notice = self.browser.find_element_by_class_name('cookies')
        if cookie_notice is not None:
            cookie_accept_button = cookie_notice.find_elements_by_class_name('cookies--button')
            if cookie_accept_button is not None and len(cookie_accept_button) > 0:
                cookie_accept_button[0].click()
                time.sleep(1)
