from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Topic(models.Model):
    sender = models.ForeignKey(
        User, verbose_name='Отправитель',
        related_name='pm_topics_sender',
        on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        User,
        verbose_name='Получатель',
        related_name='pm_topics_recipient',
        on_delete=models.CASCADE)
    subject = models.CharField('Тема', max_length=255)
    last_sent_at = models.DateTimeField()

    class Meta:
        ordering = ['-last_sent_at']

    def get_absolute_url(self):
        return 'личные сообщения', [self.pk]


class Message(models.Model):
    topic = models.ForeignKey(
        Topic, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(
        User, verbose_name='Отправитель',
        on_delete=models.CASCADE,
        related_name='messages')
    body = models.TextField('Сообщение')
    sent_at = models.DateTimeField('Опубликовано', auto_now_add=True)
    read_at = models.DateTimeField('Читать', blank=True, null=True, default=None)

    class Meta:
        ordering = ['-sent_at']

    def get_absolute_url(self):
        return '%s#message-%s' % (self.topic.get_absolute_url(), self.pk)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(
        upload_to='users/',
        default='users/avatar180.jpg',
        verbose_name='Аватарка',
        help_text='Добавьте аватарку')

    def __str__(self):
        return self.user.username


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Ссылка')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Группы'
        verbose_name = 'Группа'


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Введите пожалуйста текст вашего поста')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts', verbose_name='Автор')
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts', verbose_name='Группа',
        help_text='Выберите пожалуйста группу')
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Изображение',
        help_text='Добавьте изображение к посту')

    class Meta:
        verbose_name_plural = 'Посты'
        verbose_name = 'Пост'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments', verbose_name='Пост')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments', verbose_name='Автор')
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Введите пожалуйста текст вашего комментария')
    created = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique subscribers')]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
