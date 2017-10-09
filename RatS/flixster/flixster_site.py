from RatS.base.base_site import Site


class Flixster(Site):
    def __init__(self, args):
        self.LOGIN_PAGE = "https://www.flixster.com/login/"
        login_form_selector = "//form[@name='login']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@name='authLogin']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@name='authPass']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        super(Flixster, self).__init__(args)
        self.MY_RATINGS_URL = 'https://www.flixster.com/user/current/ratings/markup/?pagesize=100'

        account_link = self.browser.find_element_by_id('profileDropdown').find_element_by_tag_name('a')\
            .get_attribute('href')
        self.USERID = int(account_link.replace('https://www.flixster.com/user/', ''))
