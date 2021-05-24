from django import forms
from django.contrib.auth import get_user_model

from .models import Message

User = get_user_model()


class MessageSendForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('body',)


class NewTopicForm(MessageSendForm):
    subject = forms.CharField(label='Subject', required=False, initial='Без темы')

    def clean_recipient(self):
        try:
            recipient = User.objects.get(username=self.cleaned_data['recipient'])
        except User.DoesNotExist:
            raise forms.ValidationError('Имя пользователя не найдено')

        return recipient
