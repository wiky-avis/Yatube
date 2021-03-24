from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class AboutPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates_url_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech')}

    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        for template, url in AboutPagesTest.templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_about_author_page_show_correct_context(self):
        response = self.guest_client.get(reverse('about:author'))
        self.assertContains(response, 'Об авторе')

    def test_about_tech_page_show_correct_context(self):
        response = self.guest_client.get(reverse('about:tech'))
        self.assertContains(response, 'Технологии')
