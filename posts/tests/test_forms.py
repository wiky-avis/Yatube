import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
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
            b'\x0A\x00\x3B')

        cls.user = User.objects.create_user(username='vika')

        cls.user_noauthor = User.objects.create_user(username='victor')

        cls.group = Group.objects.create(
            title='Название тестовой группы',
            description='описание тестовой группы',
            slug='test-slug')

        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.user,
            group=cls.group)

    def setUp(self):
        self.client_author = Client()
        self.client_author.force_login(PostCreateFormTests.user)

        self.client_noauthor = Client()
        self.client_noauthor.force_login(PostCreateFormTests.user_noauthor)

        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PostCreateFormTests.small_gif,
            content_type='image/gif'
        )

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def create_or_edit_post(self, response, post, text, url, **kwargs):
        self.assertRedirects(response, reverse(url, **kwargs))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Post.objects.filter(
                text=text,
                group=PostCreateFormTests.group.id).exists())
        self.assertEqual(post.text, text)
        self.assertEqual(post.author, PostCreateFormTests.user)
        self.assertEqual(post.group.id, PostCreateFormTests.group.id)
        self.assertEqual(post.image, f'posts/{self.uploaded}')

    def test_create_post(self):
        form_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.id,
            'image': self.uploaded}

        response = self.client_author.post(
            reverse('new_post'),
            data=form_data,
            follow=True)

        post = Post.objects.get(text='Тестовый текст')

        self.assertEqual(Post.objects.count(), 2)
        self.create_or_edit_post(response, post, 'Тестовый текст', 'index')

    def test_edit_post_author(self):
        form_data = {
            'text': 'Текст тестового поста 444',
            'group': PostCreateFormTests.group.id,
            'image': self.uploaded}

        response = self.client_author.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': PostCreateFormTests.user.username,
                    'post_id': PostCreateFormTests.post.id}),
                data=form_data, follow=True)

        post = Post.objects.get(text='Текст тестового поста 444')

        self.assertEqual(Post.objects.count(), 1)
        self.create_or_edit_post(
            response, post,
            'Текст тестового поста 444',
            'post',
            kwargs={
                'username': PostCreateFormTests.user.username,
                'post_id': PostCreateFormTests.post.id})

    def test_edit_post_noauthor(self):
        form_data = {
            'text': 'Текст тестового поста 555',
            'group': PostCreateFormTests.group.id}

        response = self.client_noauthor.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': PostCreateFormTests.user.username,
                    'post_id': PostCreateFormTests.post.id}),
                data=form_data, follow=True)

        self.assertRedirects(response, reverse(
            'post', kwargs={
                'username': PostCreateFormTests.user.username,
                'post_id': PostCreateFormTests.post.id}))
        self.assertFalse(
            Post.objects.filter(
                text='Текст тестового поста 555',
                group=PostCreateFormTests.group.id).exists())
