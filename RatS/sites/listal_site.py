import sys
import time

from RatS.sites.base_site import Site


class Listal(Site):
    def __init__(self):
        self.LOGIN_PAGE = "https://www.listal.com/login-iframe"
        self.LOGIN_USERNAME_SELECTOR = "form input[name='username']"
        self.LOGIN_PASSWORD_SELECTOR = "form input[name='password']"
        super(Listal, self).__init__()
        self.MY_RATINGS_URL = 'http://%s.listal.com/movies/all/1/?rating=1' % self.USERNAME

    def login(self):
        sys.stdout.write('===== %s: performing login' % type(self).__name__)
        sys.stdout.flush()
        self.browser.get(self.LOGIN_PAGE)
        time.sleep(1)

        self.browser.execute_script("""
            $.post(
                'https://www.listal.com/login-ajax/',
                {
                    username: '%s',
                    password: '%s'
                },
                function(data, status) {}
            );
        """ % (self.USERNAME, self.PASSWORD))

        time.sleep(1)
        self.browser.get('http://www.listal.com/')
