from unittest import TestCase
from unittest import skip

from RatS.listal.listal_site import Listal


@skip('this test is unstable on travis')
class ListalSiteTest(TestCase):
    def setUp(self):
        self.site = Listal(None)

    def test_login(self):
        self.assertIn(self.site.USERNAME, self.site.browser.page_source)

    def tearDown(self):
        self.site.browser_handler.kill()
