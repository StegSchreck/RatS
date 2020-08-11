from unittest import TestCase
from unittest import skip

from RatS.allocine.allocine_site import AlloCine


@skip('this test is unstable on travis')
class AlloCineSiteTest(TestCase):
    def setUp(self):
        self.site = AlloCine(None)

    def test_login(self):
        self.assertIn('Votre profil public', self.site.browser.page_source)

    def tearDown(self):
        self.site.browser_handler.kill()
