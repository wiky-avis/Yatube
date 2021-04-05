from django.contrib import admin

from .models import Topic


class TopicAdmin(admin.ModelAdmin):
    list_display = ('pk', 'sender', 'recipient', 'subject', 'last_sent_at')


admin.site.register(Topic, TopicAdmin)
