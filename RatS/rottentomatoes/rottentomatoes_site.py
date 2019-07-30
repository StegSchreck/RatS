import time

from RatS.base.base_site import Site


class RottenTomatoes(Site):
    def __init__(self, args):
        login_form_selector = "//form[@id='login']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='login_username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='login_password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        super(RottenTomatoes, self).__init__(args)
        self.MY_RATINGS_URL = self._get_ratings_url()

    def _get_login_page_url(self):
        return "https://www.rottentomatoes.com/"

    def _pre_login_action(self):
        self.browser.execute_script("return $.find('#header-top-bar-login')[0].click()")
        time.sleep(1)

    def _user_is_not_logged_in(self):
        return len(self.browser.find_elements_by_xpath("//*[@id='header-top-bar-login']")) > 0

    def _get_ratings_url(self):
        time.sleep(1)  # wait for user login status to be checked
        account_link = self.browser.find_element_by_id('headerUserSection').find_element_by_tag_name('a') \
            .get_attribute('href')
        self.USERID = account_link.replace('https://www.rottentomatoes.com/user/id/', '').split('/')[0]
        return 'https://www.rottentomatoes.com/napi/userProfile/movieRatings/{user_id}'.format(
            user_id=self.USERID
        )
