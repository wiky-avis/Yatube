from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='vika')

        cls.post = Post.objects.create(
            text='Текст тестового поста', author=cls.user
        )

        cls.group = Group.objects.create(
            title='Название тестовой группы',
            description='описание тестовой группы',
            slug='test-slug'
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(PostModelTest.user)

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
            'image': 'Изображение'
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите пожалуйста текст вашего поста',
            'group': 'Выберите пожалуйста группу',
            'image': 'Добавьте изображение к посту'
        }

        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_post_name_is_text_and_group_name_is_title(self):
        post_b = Post.objects.get(text=PostModelTest.post.text)
        post_2 = Post.objects.create(
            text='Текст поста', author=PostModelTest.user)

        str_test = {
            f'{PostModelTest.post}': post_b.text[:15],
            f'{post_2}': post_2.text,
            f'{PostModelTest.group}': PostModelTest.group.title
        }

        self.assertEqual(len(str(PostModelTest.post)), 15)
        self.assertEqual(len(str(post_2)), 11)
        for value, expected in str_test.items():
            with self.subTest():
                self.assertEqual(value, expected)
