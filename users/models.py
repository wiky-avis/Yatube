from django.contrib.auth import get_user_model
from django.db import models
from datetime import datetime

User = get_user_model()


class TopicManager(models.Manager):
    def by_user(self, user):
        """
        Все топики выбранного пользователя
        """
        return self.filter(models.Q(sender=user) | models.Q(recipient=user))


class MessageManager(models.Manager):
    def count_unread(self, user, topic=None):
        """
        Количество непрочитанных сообщений
        """
        qs = self.filter(models.Q(topic__recipient=user) | models.Q(topic__sender=user), read_at__exact=None).exclude(sender=user)
        if topic is not None:
            qs = qs.filter(topic=topic)
        return qs.count()

    def by_topic(self, topic):
        """
        Все сообщение в топике
        """
        return self.select_related('sender').filter(topic=topic)

    def mark_read(self, user, topic):
        """
        Помечаем сообщения как прочитанные
        """
        self.exclude(sender=user).filter(topic=topic, read_at__exact=None).update(read_at=datetime.now())


class Topic(models.Model):
    sender = models.ForeignKey(
        User, verbose_name='Отправитель',
        related_name='pm_topics_sender',
        on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        User,
        verbose_name='Получатель',
        related_name='pm_topics_recipient',
        on_delete=models.CASCADE,
        help_text='Укажите имя получателя')
    subject = models.CharField('Тема', max_length=255, blank=True, null=True, default='Без темы')
    last_sent_at = models.DateTimeField()

    objects = TopicManager()

    class Meta:
        ordering = ['-last_sent_at']

    def count_messages(self):
        return self.topic_messages.count()

    def count_unread_messages(self):
        return self.topic_messages.filter(read_at__exact=None).count()

    def last_unread_message(self):
        try:
            return self.topic_messages.order_by('-sent_at').filter(read_at__exact=None)[0]
        except IndexError:
            return None


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

    objects = MessageManager()

    class Meta:
        ordering = ['-sent_at']
