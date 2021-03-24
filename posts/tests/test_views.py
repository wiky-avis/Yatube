import shutil
import tempfile
import time

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from django.core.cache import cache

from posts.models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.user = User.objects.create_user(
            first_name='Виктория', last_name='Аксентий', username='vika')

        cls.group = Group.objects.create(
            title='Название тестовой группы',
            description='описание тестовой группы',
            slug='test-slug')

        cls.group2 = Group.objects.create(
            title='Название тестовой группы',
            description='описание тестовой группы',
            slug='test2-slug')

        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded)

        cls.templates_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse(
                'group_posts', kwargs={'slug': cls.group.slug}),
            'posts/new_post.html': reverse('new_post')}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

        self.client_auth = Client()
        self.client_auth.force_login(PostsPagesTests.user)

    def show_correct_context_post(self, post_object):
        self.assertEqual(post_object.author, PostsPagesTests.user)
        self.assertEqual(post_object.pub_date, PostsPagesTests.post.pub_date)
        self.assertEqual(post_object.text, PostsPagesTests.post.text)
        self.assertEqual(post_object.group, PostsPagesTests.group)
        self.assertEqual(
            post_object.image, f'posts/{PostsPagesTests.uploaded}')

    def test_pages_uses_correct_template(self):
        for template, url in PostsPagesTests.templates_url_names.items():
            with self.subTest(url=url):
                response = self.client_auth.get(url)
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        response = self.client_auth.get(reverse('index'))

        post_object = response.context['page'][0]

        self.show_correct_context_post(post_object)

    def test_group_page_show_correct_context(self):
        response = self.client_auth.get(
            reverse(
                'group_posts',
                kwargs={'slug': PostsPagesTests.group.slug}))

        group_object = response.context['group']

        self.assertEqual(group_object.title, PostsPagesTests.group.title)
        self.assertEqual(
            group_object.description, PostsPagesTests.group.description)

        post_object = response.context['page'][0]

        self.show_correct_context_post(post_object)

    def test_new_post_show_correct_context(self):
        response = self.client_auth.get(reverse('new_post'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField}

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_new_post_appears_on_pages(self):
        url_pages = (
            reverse('index'),
            reverse(
                'group_posts', kwargs={'slug': PostsPagesTests.group.slug}),
            reverse(
                'profile', kwargs={'username': PostsPagesTests.user.username}),
            reverse(
                'post',
                kwargs={
                    'username': PostsPagesTests.user.username,
                    'post_id': PostsPagesTests.post.id}))

        for url in url_pages:
            with self.subTest(value=url):
                response = self.client_auth.get(url)
                self.assertContains(response, PostsPagesTests.post.text)

    def test_new_post_not_appear_on_page_group2(self):
        response = self.client_auth.get(
            reverse(
                'group_posts', kwargs={'slug': PostsPagesTests.group2.slug}))

        self.assertNotContains(response, PostsPagesTests.post.text)

    def test_username_page_show_correct_context(self):
        response = self.guest_client.get(
            reverse(
                'profile',
                kwargs={'username': PostsPagesTests.user.username}))

        profile_object = response.context['profile']

        self.assertEqual(
            profile_object.get_full_name(),
            PostsPagesTests.user.get_full_name())
        self.assertEqual(
            profile_object.username, PostsPagesTests.user.username)
        self.assertEqual(
            profile_object.posts.count(), PostsPagesTests.user.posts.count())

        post_object = response.context['page'][0]

        self.show_correct_context_post(post_object)

    def test_post_view_page_show_correct_context(self):
        response = self.guest_client.get(
            reverse(
                'post',
                kwargs={
                    'username': PostsPagesTests.user.username,
                    'post_id': PostsPagesTests.post.id}))

        profile_object = response.context['profile']

        self.assertEqual(
            profile_object.get_full_name(),
            PostsPagesTests.user.get_full_name())
        self.assertEqual(
            profile_object.username, PostsPagesTests.user.username)
        self.assertEqual(
            profile_object.posts.count(), PostsPagesTests.user.posts.count())

        post_object = response.context['post']

        self.show_correct_context_post(post_object)

    def test_post_edit_show_correct_context(self):
        response = self.client_auth.get(
            reverse(
                'post_edit',
                kwargs={
                    'username': PostsPagesTests.user.username,
                    'post_id': PostsPagesTests.post.id}))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField}

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='vika')

        cls.group = Group.objects.create(
            title='Название тестовой группы',
            description='описание тестовой группы',
            slug='test-slug')

        objs = [Post(
            text=f'Текст тестового поста {i}',
            author=cls.user,
            group=cls.group) for i in range(13)]
        Post.objects.bulk_create(objs)

    def setUp(self):
        self.client_auth = Client()
        self.client_auth.force_login(PaginatorViewsTest.user)

    def test_index_and_group_second_page_containse_three_records(self):
        response_pages = (self.client_auth.get(
            reverse('index') + '?page=2'),
            self.client_auth.get(
            reverse(
                'group_posts',
                kwargs={'slug': PaginatorViewsTest.group.slug}) + '?page=2'))

        for response in response_pages:
            with self.subTest():
                self.assertEqual(
                    len(response.context.get('page').object_list), 3)

    def test_index_and_group_first_page_containse_ten_records(self):
        response_pages = (
            self.client_auth.get(reverse('index')),
            self.client_auth.get(reverse(
                'group_posts',
                kwargs={'slug': PaginatorViewsTest.group.slug})))

        for response in response_pages:
            with self.subTest():
                self.assertEqual(
                    len(response.context.get('page').object_list), 10)


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='vika')

    def setUp(self):
        self.client = Client()
        self.client.force_login(TestCache.user)

    def tearDown(self):
        cache.clear()

    def test_cache_index_page(self):
        post = Post.objects.create(text='проверка кэша', author=TestCache.user)

        cache.set('index_page', post, 20)

        response = cache.get('index_page')
        self.assertEqual(response, post)

        response2 = self.client.get(reverse('index'))
        self.assertContains(response2, post.text)

        time.sleep(25)

        response = cache.get('index_page')
        self.assertNotEqual(str(response), post.text)

        response2 = self.client.get(reverse('index'))
        self.assertContains(response2, post.text)

    def test_cache_index_page_creatе_two_posts(self):
        self.client.post(
            reverse('new_post'),
            data={'author': TestCache.user, 'text': 'проверка кэша'})

        response = self.client.get(reverse('index'))
        self.assertContains(response, 'проверка кэша')

        self.client.post(
            reverse('new_post'),
            data={'author': TestCache.user, 'text': 'проверка кэша 2'}
            )

        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'проверка кэша 2')
