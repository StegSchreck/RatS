import time

from selenium.webdriver.common.by import By

from RatS.base.base_exceptions import CaptchaPresentException
from RatS.base.base_site import BaseSite


class IMDB(BaseSite):
    def __init__(self, args):
        login_form_selector = "//form[@name='signIn']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='ap_email']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='ap_password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@id='signInSubmit']"
        super(IMDB, self).__init__(args)
        self.MY_RATINGS_URL = "https://www.imdb.com/list/ratings"

        if not self.CREDENTIALS_VALID:
            return

        time.sleep(1)

    def _get_login_page_url(self):
        return "https://www.imdb.com/ap/signin?openid.return_to=https%3A%2F%2Fwww.imdb.com%2Fap-signin-handler&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=imdb_us&openid.mode=checkid_setup&siteState=eyJvcGVuaWQuYXNzb2NfaGFuZGxlIjoiaW1kYl91cyIsInJlZGlyZWN0VG8iOiJodHRwczovL3d3dy5pbWRiLmNvbS8_cmVmXz1sb2dpbiJ9&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&&tag=imdbtag_reg-20"  # noqa: E501

    def _handle_captcha_challenge_if_present(self):
        if len(self.browser.find_elements(By.XPATH, "//div[@id='auth-captcha-image-container']")) > 0:
            # time.sleep(30)  # activate this line and handle the captcha manually once using the -x command line option
            self.browser_handler.kill()
            raise CaptchaPresentException(
                f"Login to {self.site_name} failed.\r\n"
                "There seems to be a Captcha challenge present for the login. Please try again later.\r\n"
                "You can also insert a timeout in the code and use the '-x' command line argument "
                "to handle the captcha manually once."
            )

    @classmethod
    def normalize_imdb_id(cls, imdb_id: str) -> int:
        return int(imdb_id.replace("tt", ""))
