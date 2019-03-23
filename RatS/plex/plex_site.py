import re
import time

from selenium.webdriver.support import ui

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
        self.PLEX_TOKEN = self._determine_plex_token()
        self.SERVER_ID = self._determine_server_id()
        self.MY_RATINGS_URL = 'http://{base_url}/library/all?type=1&userRating!=0' \
                              '&X-Plex-Container-Start={page_start}' \
                              '&X-Plex-Container-Size={page_size}' \
                              '&X-Plex-Token={plex_token}'.format(
                                  base_url=self.BASE_URL,
                                  page_start=0,
                                  page_size=100,
                                  plex_token=self.PLEX_TOKEN
                              )

    def _determine_plex_token(self):
        self.browser.get('http://{base_url}/web/index.html#'.format(base_url=self.BASE_URL))
        wait = ui.WebDriverWait(self.browser, 600)
        wait.until(lambda driver: driver.find_element_by_xpath("//button[@data-qa-id='metadataPosterMoreButton']"))

        self.browser.find_elements_by_xpath("//button[@data-qa-id='metadataPosterMoreButton']")[0].click()
        self.browser.find_elements_by_xpath("//button[@role='menuitem']")[-1].click()
        link_to_xml = self.browser.find_element_by_xpath("//div[@class='modal-footer']//a").get_attribute('href')
        plex_token = re.findall(r'X-Plex-Token=(\w+)', link_to_xml)[0]

        return plex_token

    def _determine_server_id(self):
        self.browser.get('http://{base_url}/web/index.html#!/settings/server'.format(base_url=self.BASE_URL))
        time.sleep(2)
        return self.browser.current_url.split('/')[-2]
