import datetime
import os
import time

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Firefox, FirefoxOptions
from xvfbwrapper import Xvfb
from selenium.webdriver.firefox.service import Service

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S")
EXPORTS_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "RatS", "exports")
)


class BrowserHandler:
    def __init__(self, args):
        self.args = args
        if self.args and not self.args.show_browser:
            self.display = Xvfb()
            self.display.start()

        log_level = self._define_log_level(self.args)
        options = self._create_browser_options(log_level)
        service = Service(log_path=f"{TIMESTAMP}_geckodriver.log")

        self.browser = Firefox(
            options=options,
            service=service,
        )
        # https://stackoverflow.com/questions/42754877/cant-upload-file-using-selenium-with-python-post-post-session-b90ee4c1-ef51-4  # pylint: disable=line-too-long
        self.browser._is_remote = False  # pylint: disable=protected-access
        self.browser.maximize_window()

    @staticmethod
    def _define_log_level(args):
        if args and args.verbose and args.verbose >= 3:
            log_level = "trace"
        elif args and args.verbose and args.verbose == 2:
            log_level = "debug"
        elif args and args.verbose and args.verbose == 1:
            log_level = "info"
        else:
            log_level = "warn"

        return log_level

    @staticmethod
    def _create_browser_options(log_level):
        options = FirefoxOptions()

        options.log.level = log_level
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", EXPORTS_FOLDER)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk", "text/csv, application/zip"
        )
        options.set_preference("browser.helperApps.alwaysAsk.force", False)
        options.set_preference("devtools.jsonview.enabled", False)
        options.set_preference("media.volume_scale", "0.0")
        # https://github.com/mozilla/geckodriver/issues/858#issuecomment-322512336
        options.set_preference("dom.file.createInChild", True)

        return options

    def kill(self):
        self.browser.service.stop()
        self.browser.stop_client()
        self.browser.close()
        try:
            self.browser.quit()
        except WebDriverException:
            pass

        if self.args and not self.args.show_browser:
            self.display.stop()
