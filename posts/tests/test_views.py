import os
import shutil

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post
from yatube.settings import BASE_DIR

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
        response = self.client.get(
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
        response = self.client.get(
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


@override_settings(MEDIA_ROOT=os.path.join(BASE_DIR, 'temp_dir'))
class ImgPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

    def test_pages_show_correct_context(self):
        url_list = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': ImgPagesTests.group.slug}),
            reverse(
                'profile', kwargs={'username': ImgPagesTests.user.username}))

        for url in url_list:
            with self.subTest():
                response = self.client.get(url)
                self.assertEqual(
                    response.context['page'][0].image,
                    f'posts/{ImgPagesTests.uploaded}')

        response = self.client.get(
            reverse(
                'post',
                kwargs={
                    'username': ImgPagesTests.user.username,
                    'post_id': ImgPagesTests.post.id}))

        self.assertEqual(
            response.context['post'].image, f'posts/{ImgPagesTests.uploaded}')


class PaginatorViewsTest(TestCase):

    def test_index_and_group_second_page_contains_ten_and_three_records(self):
        user = User.objects.create_user(username='vika')
        self.client.force_login(user)

        group = Group.objects.create(
            title='Название тестовой группы',
            slug='test-slug')

        ten_records = 10
        three_records = 3
        objs = [
            Post(
                text=f'Текст тестового поста {i}',
                author=user,
                group=group) for i in range(ten_records + three_records)]
        Post.objects.bulk_create(objs)

        response_pages = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': group.slug}))

        pages_list = {f'{ten_records}': 1, f'{three_records}': 2}

        for magic, i in pages_list.items():
            for page in response_pages:
                response = self.client.get(page, {'page': f'{i}'})
                with self.subTest():
                    self.assertEqual(
                        len(response.context.get('page').object_list),
                        int(magic))


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='vika')

    def test_cache_index_page(self):
        post = Post.objects.create(text='проверка кэша', author=TestCache.user)

        cache.set('index_page', post, 20)

        response = cache.get('index_page')
        self.assertEqual(response, post)

        response2 = self.client.get(reverse('index'))
        self.assertContains(response2, post.text)

        cache.clear()

        response = cache.get('index_page')
        self.assertNotEqual(str(response), post.text)

        response2 = self.client.get(reverse('index'))
        self.assertContains(response2, post.text)

    def test_cache_index_page_creatе_two_posts(self):
        post = Post.objects.create(author=TestCache.user, text='проверка кэша')

        response = self.client.get(reverse('index'))
        self.assertContains(response, post.text)

        post_two = Post.objects.create(
            author=TestCache.user, text='проверка кэша 2')

        response = self.client.get(reverse('index'))
        self.assertNotContains(response, post_two.text)


class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create_user(username='vika')

        cls.user_following = User.objects.create_user(username='victor')

        cls.post = Post.objects.create(
            text='Новая запись появляется в ленте подписчиков',
            author=TestFollow.user_following)

    def setUp(self):
        self.client_auth = Client()
        self.client_auth.force_login(TestFollow.user_follower)

    def test_follow_authorized_user(self):
        self.client_auth.get(reverse(
            'profile_follow', kwargs={
                'username': TestFollow.user_following.username}))

        self.assertEqual(Follow.objects.count(), 1)

    def test_unfollow_authorized_user(self):
        self.client_auth.get(reverse(
            'profile_unfollow', kwargs={
                'username': TestFollow.user_following.username}))

        self.assertEqual(Follow.objects.count(), 0)

    def test_follow_not_authorized_user(self):
        response = self.client.get(reverse(
            'profile_follow', kwargs={
                'username': TestFollow.user_following.username}))

        kw = {'username': TestFollow.user_following.username}
        reverse_login = reverse('login')
        reverse_follow = reverse('profile_follow', kwargs=kw)

        self.assertRedirects(
            response, f'{reverse_login}?next={reverse_follow}')

    def test_check_new_post_from_follower(self):
        Follow.objects.create(
            user=TestFollow.user_follower, author=TestFollow.user_following)

        response = self.client_auth.get(reverse('follow_index'))
        self.assertContains(response, TestFollow.post.text)

    def test_check_new_post_from_not_follower(self):
        user_not_follower = User.objects.create_user(username='zhanna')
        self.client.force_login(user_not_follower)

        response = self.client.get(reverse('follow_index'))
        self.assertNotContains(response, TestFollow.post.text)


class TestComment(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='vika')

        cls.post = Post.objects.create(text='Просто текст', author=cls.user)

    def test_authorized_user_comments_posts(self):
        self.client.force_login(TestComment.user)

        self.client.post(
            reverse(
                'add_comment',
                kwargs={
                    'username': TestComment.user.username,
                    'post_id': TestComment.post.id}),
                data={'text': 'Комментарий авторизированного пользователя'},
                follow=True)

        self.assertTrue(
            Comment.objects.filter(
                text='Комментарий авторизированного пользователя',
                post_id=TestComment.post.id).exists())

    def test_comment_notauthorized(self):
        self.client.post(
            reverse(
                'add_comment',
                kwargs={
                    'username': TestComment.user.username,
                    'post_id': TestComment.post.id}),
                data={'text': 'Комментарий неавторизированного пользователя'},
                follow=True)

        self.assertFalse(
            Comment.objects.filter(
                text='Комментарий неавторизированного пользователя',
                post_id=TestComment.post.id).exists())
