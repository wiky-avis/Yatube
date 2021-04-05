from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Message, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ['text']


class MessageSendForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('body',)


class NewTopicForm(MessageSendForm):
    recipient = forms.CharField(label='Recipient', help_text='Укажите имя пользователя')
    subject = forms.CharField(label='Subject')

    def clean_recipient(self):
        try:
            recipient = User.objects.get(username=self.cleaned_data['recipient'])
        except User.DoesNotExist:
            raise forms.ValidationError('Имя пользователя не найдено')

        return recipient
