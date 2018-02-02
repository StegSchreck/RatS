import sys
import time

from RatS.base.base_site import Site


class Listal(Site):
    def __init__(self, args):
        login_form_selector = "//form[contains(concat(' ', normalize-space(@class), ' '), ' login-form ')]"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@name='username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@name='password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + \
            "//button[contains(concat(' ', normalize-space(@class), ' '), ' submit ')]"
        super(Listal, self).__init__(args)
        self.MY_RATINGS_URL = 'http://{username}.listal.com/movies/all/1/?rating=1'.format(username=self.USERNAME)

    def _get_login_page_url(self):
        return "https://www.listal.com/login-iframe"

    def login(self):
        sys.stdout.write('===== {site_displayname}: performing login'.format(site_displayname=self.site_displayname))
        sys.stdout.flush()
        self.browser.get(self.LOGIN_PAGE)
        time.sleep(1)

        self.browser.execute_script("""
            $.post(
                'https://www.listal.com/login-ajax/',
                {{
                    username: '{username}',
                    password: '{password}'
                }},
                function(data, status) {{}}
            );
        """.format(username=self.USERNAME, password=self.PASSWORD))

        time.sleep(1)
        self.browser.get('http://www.listal.com/')
