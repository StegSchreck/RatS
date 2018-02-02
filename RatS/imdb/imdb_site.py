import time

from selenium.common.exceptions import NoSuchElementException

from RatS.base.base_site import Site


class IMDB(Site):
    def __init__(self, args):
        login_form_selector = "//form[@name='signIn']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='ap_email']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='ap_password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@id='signInSubmit']"
        super(IMDB, self).__init__(args)
        self.MY_RATINGS_URL = ''
        time.sleep(1)

        iteration = 0
        while self.MY_RATINGS_URL == '':
            try:
                self._get_ratings_url()
                break
            except NoSuchElementException as e:
                iteration += 1
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue

    def _get_login_page_url(self):
        return "https://www.imdb.com/ap/signin?openid.return_to=https%3A%2F%2Fwww.imdb.com%2Fap-signin-handler&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=imdb_us&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"   # pylint: disable=line-too-long

    def _get_ratings_url(self):
        account_link = self.browser.find_element_by_id('consumer_user_nav').find_element_by_tag_name('a') \
            .get_attribute('href')
        self.USERID = account_link.replace('http://www.imdb.com/user/', '').split('/')[0]
        self.MY_RATINGS_URL = 'http://www.imdb.com/user/{user_id}/ratings'.format(user_id=self.USERID)
