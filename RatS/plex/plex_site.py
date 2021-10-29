import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui

from RatS.base.base_site import BaseSite


class Plex(BaseSite):
    def __init__(self, args):
        login_form_selector = "//form"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='email']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        self.LOGIN_METHOD_EMAIL_SELECTOR = "//button[@data-qa-id='signIn--email']"
        super(Plex, self).__init__(args)

    def _get_login_page_url(self):
        self.BASE_URL = f"{self.config[self.site_name]['BASE_URL']}:{self.config[self.site_name]['BASE_PORT']}"
        return f"http://{self.BASE_URL}/web/index.html#!/login"

    def _insert_login_credentials(self):
        time.sleep(2)
        self.browser.find_element(By.XPATH, self.LOGIN_METHOD_EMAIL_SELECTOR).click()
        time.sleep(0.5)
        BaseSite._insert_login_credentials(self)

    def _user_is_not_logged_in(self):
        return self.USERNAME not in self.browser.page_source

    def _parse_configuration(self):
        self.PLEX_TOKEN = self._determine_plex_token()
        self.SERVER_ID = self._determine_server_id()
        self.MY_RATINGS_URL = (
            f"http://{self.BASE_URL}/library/all?type=1&userRating!=0"
            f"&X-Plex-Container-Start=0"
            f"&X-Plex-Container-Size=100"
            f"&X-Plex-Token={self.PLEX_TOKEN}"
        )

    def _determine_plex_token(self):
        self.browser.get(f"http://{self.BASE_URL}/web/index.html#'")
        wait = ui.WebDriverWait(self.browser, 600)
        wait.until(
            lambda driver: driver.find_element(
                By.XPATH, "//button[@data-qa-id='metadataPosterMoreButton']"
            )
        )

        self.browser.find_elements(
            By.XPATH, "//button[@data-qa-id='metadataPosterMoreButton']"
        )[0].click()
        self.browser.find_elements(By.XPATH, "//button[@role='menuitem']")[-1].click()
        link_to_xml = self.browser.find_element(
            By.XPATH, "//div[@class='modal-footer']//a"
        ).get_attribute("href")
        plex_token = re.findall(r"X-Plex-Token=(\w+)", link_to_xml)[0]

        return plex_token

    def _determine_server_id(self):
        self.browser.get(f"http://{self.BASE_URL}/web/index.html#!/settings/server")
        time.sleep(2)
        return self.browser.current_url.split("/")[-2]
