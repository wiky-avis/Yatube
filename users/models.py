from django.contrib.auth import get_user_model
from django.db import models

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
        Topic, related_name='topic_messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(
        User, verbose_name='Отправитель',
        on_delete=models.CASCADE,
        related_name='sender_messages')
    body = models.TextField('Сообщение')
    sent_at = models.DateTimeField('Опубликовано', auto_now_add=True)
    read_at = models.DateTimeField('Читать', blank=True, null=True, default=None)

    class Meta:
        ordering = ['-sent_at']

    def get_absolute_url(self):
        return '%s#message-%s' % (self.topic.get_absolute_url(), self.pk)
