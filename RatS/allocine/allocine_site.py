import time

from selenium.common.exceptions import NoSuchElementException

from RatS.base.base_site import Site


class AlloCine(Site):
    def __init__(self, args):
        login_form_selector = "//form[@name='sign_in']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='sign_in__username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='sign_in__password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        super(AlloCine, self).__init__(args)
        self.MY_RATINGS_URL = ''
        self.USER_ID = ''
        time.sleep(1)

        iteration = 0
        while self.MY_RATINGS_URL == '':
            iteration += 1
            try:
                self._get_ratings_url()
                break
            except NoSuchElementException as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration)
                continue

        self.handle_privacy_notice_if_present()

    def _get_login_page_url(self):
        return "https://mon.allocine.fr/connexion/"

    def _get_ratings_url(self):
        account_link = self.browser.find_element_by_css_selector('a.icon-profil').get_attribute('href')
        self.USER_ID = account_link.replace('http://www.allocine.fr/', '').split('/')[0]
        self.MY_RATINGS_URL = 'http://www.allocine.fr/{user_id}/films/'.format(user_id=self.USER_ID)

    def handle_privacy_notice_if_present(self):
        cookie_notices = self.browser.find_elements_by_id('qcCmpUi')
        if len(cookie_notices) == 0:
            return
        cookie_notice = cookie_notices[0]
        if cookie_notice is not None:
            cookie_accept_button = cookie_notice.find_elements_by_class_name('qc-cmp-button')
            if cookie_accept_button is not None and len(cookie_accept_button) > 1:
                cookie_accept_button[1].click()
                time.sleep(1)
