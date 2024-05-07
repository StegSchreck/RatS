import datetime
import os
import time

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Firefox, FirefoxOptions
from xvfbwrapper import Xvfb
from selenium.webdriver.firefox.service import Service

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S")
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "RatS", "exports"))


class BrowserHandler:
    def __init__(self, args):
        self.args = args
        if self.args and not self.args.show_browser:
            self.display = Xvfb()
            self.display.start()

        log_level = self._define_log_level(self.args.log) if self.args and self.args.log else "warn"

        options = self._create_browser_options(log_level)
        service = Service(log_path=f"{TIMESTAMP}_geckodriver.log")

        self.browser = Firefox(options=options, service=service)
        # https://stackoverflow.com/questions/42754877/cant-upload-file-using-selenium-with-python-post-post-session-b90ee4c1-ef51-4  # noqa: E501
        self.browser._is_remote = False  # pylint: disable=protected-access
        self.browser.maximize_window()

    @staticmethod
    def _define_log_level(log_level: str) -> str:
        match log_level:
            case "DEBUG":
                return "debug"
            case "INFO":
                return "info"
            case _:
                return "warn"

    @staticmethod
    def _create_browser_options(log_level) -> FirefoxOptions:
        options = FirefoxOptions()

        options.log.level = log_level
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", EXPORTS_FOLDER)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv, application/zip")
        options.set_preference("browser.helperApps.alwaysAsk.force", False)
        options.set_preference("devtools.jsonview.enabled", False)
        options.set_preference("media.volume_scale", "0.0")
        # https://github.com/mozilla/geckodriver/issues/858#issuecomment-322512336
        options.set_preference("dom.file.createInChild", True)

        return options

    def kill(self) -> None:
        self.browser.stop_client()
        self.browser.close()
        try:
            self.browser.quit()
        except WebDriverException:
            pass
        self.browser.service.stop()

        if self.args and not self.args.show_browser:
            self.display.stop()
