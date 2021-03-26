from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus

User = get_user_model()


class AboutStaticUrls(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'}

    def setUp(self):
        self.guest_client = Client()

    def test_urls_uses_correct_template(self):
        for template, url in AboutStaticUrls.templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_availability_for_guest_user(self):
        for template, url in AboutStaticUrls.templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
