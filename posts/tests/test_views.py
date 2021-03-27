import shutil
import tempfile
import time

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
            group=cls.group)

        cls.templates_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse(
                'group_posts', kwargs={'slug': cls.group.slug}),
            'posts/new_post.html': reverse('new_post')}

    def setUp(self):
        self.guest_client = Client()

        self.client_auth = Client()
        self.client_auth.force_login(PostsPagesTests.user)

    def show_correct_context_post(self, post_object):
        self.assertEqual(post_object.author, PostsPagesTests.user)
        self.assertEqual(post_object.pub_date, PostsPagesTests.post.pub_date)
        self.assertEqual(post_object.text, PostsPagesTests.post.text)
        self.assertEqual(post_object.group, PostsPagesTests.group)

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


class ImgPagesTests(TestCase):
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
            content_type='image/gif')

        cls.user = User.objects.create_user(username='vika')

        cls.group = Group.objects.create(
            title='Группа',
            slug='test-slug')

        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.client = Client()

    def test_index_pages_show_correct_context(self):
        response = self.client.get(reverse('index'))

        post_object = response.context['page'][0]

        self.assertEqual(
            post_object.image, f'posts/{ImgPagesTests.uploaded}')

    def test_group_page_show_correct_context(self):
        response = self.client.get(
            reverse(
                'group_posts',
                kwargs={'slug': ImgPagesTests.group.slug}))

        post_object = response.context['page'][0]

        self.assertEqual(
            post_object.image, f'posts/{ImgPagesTests.uploaded}')

    def test_username_page_show_correct_context(self):
        response = self.client.get(
            reverse(
                'profile',
                kwargs={'username': ImgPagesTests.user.username}))

        post_object = response.context['page'][0]

        self.assertEqual(
            post_object.image, f'posts/{ImgPagesTests.uploaded}')

    def test_post_view_page_show_correct_context(self):
        response = self.client.get(
            reverse(
                'post',
                kwargs={
                    'username': ImgPagesTests.user.username,
                    'post_id': ImgPagesTests.post.id}))

        post_object = response.context['post']

        self.assertEqual(
            post_object.image, f'posts/{ImgPagesTests.uploaded}')


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

    def test_index_and_group_second_page_contains_three_records(self):
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

    def test_index_and_group_first_page_contains_ten_records(self):
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

        response = cache.delete('index_page')

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
            data={'author': TestCache.user, 'text': 'проверка кэша 2'})

        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'проверка кэша 2')


class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create_user(username='vika')

        cls.user_following = User.objects.create_user(username='victor')

        cls.user_follower_2 = User.objects.create_user(username='zhanna')

    def setUp(self):
        self.user_not_authorized = Client()

        self.client_follower = Client()
        self.client_follower.force_login(TestFollow.user_follower)

        self.client_following = Client()
        self.client_following.force_login(TestFollow.user_following)

        self.client_follower_2 = Client()
        self.client_follower_2.force_login(TestFollow.user_follower_2)

    def test_follow_unfollow_authorized_user(self):
        self.client_follower.get(reverse(
            'profile_follow', kwargs={
                'username': TestFollow.user_following.username}))

        response = self.client_follower.get(reverse(
            'profile', kwargs={
                'username': TestFollow.user_following.username}))

        self.assertEqual(response.context['following_count'], 1)

        self.client_follower.get(reverse(
            'profile_unfollow', kwargs={
                'username': TestFollow.user_following.username}))

        response = self.client_follower.get(reverse(
            'profile', kwargs={
                'username': TestFollow.user_following.username}))

        self.assertEqual(response.context['following_count'], 0)

    def test_follow_not_authorized_user(self):
        self.user_not_authorized.get(reverse(
            'profile_follow', kwargs={
                'username': TestFollow.user_following.username}))

        response = self.user_not_authorized.get(reverse(
            'profile', kwargs={
                'username': TestFollow.user_following.username}))

        self.assertEqual(response.context['following_count'], 0)

    def test_check_new_post_from_follower(self):
        self.client_follower.get(reverse(
            'profile_follow', kwargs={
                'username': TestFollow.user_following.username}))

        post_data = {'text': 'Новая запись появляется в ленте подписчиков'}
        self.client_following.post(
            reverse('new_post'),
            data=post_data,
            follow=True)

        response = self.client_follower.get(reverse('follow_index'))
        self.assertContains(response, post_data['text'])

        response = self.client_follower_2.get(reverse('follow_index'))
        self.assertNotContains(response, post_data['text'])


class TestComment(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='vika')

        cls.post = Post.objects.create(text='Просто текст', author=cls.user)

    def setUp(self):
        self.user_not_authorized = Client()

        self.client_user = Client()
        self.client_user.force_login(TestComment.user)

    def test_authorized_user_comments_posts(self):
        self.client_user.post(
            reverse(
                'add_comment',
                kwargs={
                    'username': TestComment.user.username,
                    'post_id': TestComment.post.id}),
                data={'text': 'Комментарий авторизированного пользователя'},
                follow=True)

        response = self.client_user.get(reverse(
            'post',
            kwargs={
                'username': TestComment.user.username,
                'post_id': TestComment.post.id}))

        self.assertContains(
            response, 'Комментарий авторизированного пользователя')

    def test_comment_notauthorized(self):
        self.user_not_authorized.post(
            reverse(
                'add_comment',
                kwargs={
                    'username': TestComment.user.username,
                    'post_id': TestComment.post.id}),
                data={'text': 'Комментарий неавторизированного пользователя'},
                follow=True)

        response = self.client_user.get(reverse(
            'post',
            kwargs={
                'username': TestComment.user.username,
                'post_id': TestComment.post.id}))

        self.assertNotContains(
            response, 'Комментарий неавторизированного пользователя')
