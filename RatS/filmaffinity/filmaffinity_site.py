import time

from RatS.base.base_site import Site


class FilmAffinity(Site):
    def __init__(self, args):
        login_form_selector = "//form[@id='login-form']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@name='username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@name='password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"
        super(FilmAffinity, self).__init__(args)
        self.MY_RATINGS_URL = 'https://www.filmaffinity.com/en/myvotes.php'

    def _get_login_page_url(self):
        return "https://www.filmaffinity.com/en/login.php"

    def _handle_cookie_notice_if_present(self):
        if len(self.browser.find_elements_by_id('info-cookie')) == 0:
            return
        cookie_notice = self.browser.find_element_by_id('info-cookie')
        if cookie_notice is not None:
            cookie_accept_button = cookie_notice.find_elements_by_class_name('cookies-y')
            if cookie_accept_button is not None and len(cookie_accept_button) > 0:
                cookie_accept_button[0].click()
                time.sleep(1)
