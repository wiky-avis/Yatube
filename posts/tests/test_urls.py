from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='victoria')

        cls.group = Group.objects.create(
            title='Название тестовой группы',
            description='описание тестовой группы',
            slug='test-slug')
        cls.group_slug = cls.group.slug

        cls.post = Post.objects.create(
            text='Текст тестового поста', author=cls.user, group=cls.group)
        cls.post_author = cls.post.author.username
        cls.post_id = cls.post.id

        cls.templates_url_names = {
            '/': 'index.html',
            f'/group/{cls.group.slug}/': 'group.html',
            f'/{cls.user.username}/': 'posts/profile.html',
            '/new/': 'posts/new_post.html'}
        cls.url = f'/{cls.post_author}/{cls.post_id}/edit/'

        cls.url_pages = [
            '/',
            f'/group/{cls.group_slug}/',
            f'/{cls.post_author}/',
            f'/{cls.post_author}/{cls.post_id}/']

    def setUp(self):
        self.client_noauthor_auth = Client()
        self.user = User.objects.create_user(username='victor')
        self.client_noauthor_auth.force_login(self.user)

        self.client_author_auth = Client()
        self.client_author_auth.force_login(StaticURLTests.user)

    def test_page_availability_for_guest_user(self):
        for url in StaticURLTests.url_pages:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_new_availability_for_authorized_user(self):
        response = self.client_noauthor_auth.get('/new/')

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        url = StaticURLTests.url
        StaticURLTests.templates_url_names[url] = 'posts/new_post.html'

        for url, template in StaticURLTests.templates_url_names.items():
            with self.subTest(url=url):
                response = self.client_author_auth.get(url)
                self.assertTemplateUsed(response, template)

    def test_username_page_availability_for_author_post(self):
        StaticURLTests.url_pages.append(StaticURLTests.url)

        for url in StaticURLTests.url_pages:
            with self.subTest(value=url):
                response = self.client_author_auth.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_page_availability_for_noauthor_post(self):
        for url in StaticURLTests.url_pages:
            with self.subTest(value=url):
                response = self.client_noauthor_auth.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_page_availability_for_guest_user(self):
        for url in StaticURLTests.url_pages:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_from_page_new_works_correctly_for_guest_user(self):
        response = self.client.get('/new/')

        reverse_login = reverse('login')
        reverse_new_post = reverse('new_post')

        self.assertRedirects(
            response, f'{reverse_login}?next={reverse_new_post}')

    def test_redirect_from_page_post_edit_works_correctly_for_noauthor(self):
        response = self.client_noauthor_auth.get(StaticURLTests.url)

        self.assertRedirects(response, reverse(
            'post', kwargs={
                'username': StaticURLTests.user.username,
                'post_id': StaticURLTests.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_redirect_from_page_post_edit_works_correctly_for_guest_user(self):
        response = self.client.get(StaticURLTests.url)

        kw = {
            'username': StaticURLTests.post_author,
            'post_id': StaticURLTests.post_id}
        reverse_login = reverse('login')
        reverse_post_edit = reverse('post_edit', kwargs=kw)

        self.assertRedirects(
            response, (
                f'{reverse_login}?next={reverse_post_edit}'))


class TestPage404(TestCase):

    def test_page_return_404(self):
        response = self.client.get('/page_not_found/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
