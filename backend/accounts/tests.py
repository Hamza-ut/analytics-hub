from django.test import TestCase, SimpleTestCase
from django.urls import reverse # decouples urls and depends on the name of the url instead of the actual url


class TestHomePage(SimpleTestCase):
    def setUp(self):
        self.response = self.client.get(reverse('home'))

    
    def test_homeview_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_homeview_uses_correct_template(self):
        self.assertTemplateUsed(self.response, 'index.html')



