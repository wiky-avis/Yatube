from django.contrib import admin

from .models import Topic, Message


class TopicAdmin(admin.ModelAdmin):
    list_display = ('pk', 'sender', 'recipient', 'subject', 'last_sent_at')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'topic', 'sender', 'body', 'sent_at', 'read_at')


admin.site.register(Message, MessageAdmin)
admin.site.register(Topic, TopicAdmin)
