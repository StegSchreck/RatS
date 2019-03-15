import sys
import time

from bs4 import BeautifulSoup

from RatS.base.base_site import Site


class Plex(Site):
    def __init__(self, args):
        login_form_selector = "//form"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='email']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        self.LOGIN_METHOD_EMAIL_SELECTOR = "//button[@data-qa-id='signIn--email']"
        super(Plex, self).__init__(args)

    def _get_login_page_url(self):
        self.BASE_URL = self.config[self.site_name]['BASE_URL'] + ":" + self.config[self.site_name]['BASE_PORT']
        return "http://{base_url}/web/index.html#!/login".format(base_url=self.BASE_URL)

    def _insert_login_credentials(self):
        time.sleep(2)
        self.browser.find_element_by_xpath(self.LOGIN_METHOD_EMAIL_SELECTOR).click()
        time.sleep(0.5)
        Site._insert_login_credentials(self)

    def _user_is_not_logged_in(self):
        return self.USERNAME not in self.browser.page_source

    def _parse_configuration(self):
        self.SERVER_ID = self._determine_server_id()
        self.MY_RATINGS_URL = 'http://{base_url}/web/index.html#!/server/{server_id}/list' \
                              '?key=%2Fhubs%2Fhome%2FrecentlyAdded%3Ftype%3D1&type=movie'.format(
                                  base_url=self.BASE_URL,
                                  server_id=self.SERVER_ID
                              )

    def _determine_movies_section_id(self):
        sys.stdout.write('\r===== ' + self.site_displayname + ': determine movie section')
        sys.stdout.flush()

        self.browser.get('http://{base_url}/web/index.html#'.format(base_url=self.BASE_URL))
        time.sleep(1)
        homepage = BeautifulSoup(self.browser.page_source, 'html.parser')
        time.sleep(1)

        library_navigation_links = homepage.find('div', attrs={'data-qa-id': 'sidebarLibrariesList'})
        movie_section = library_navigation_links.find('i', class_='plex-icon-movies-560').parent.parent.parent

        return movie_section['data-qa-id'].split('--')[-1]

    def _determine_server_id(self):
        self.browser.get('http://{base_url}/web/index.html#!/settings/server'.format(base_url=self.BASE_URL))
        time.sleep(1)
        return self.browser.current_url.split('/')[-2]
