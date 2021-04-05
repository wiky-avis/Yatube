from string import Template

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.safestring import mark_safe
from posts.models import Profile
from .models import Message, Topic

User = get_user_model()


class PictureWidget(forms.widgets.FileInput):
    """Виджет для отображения превью картинки в форме"""
    def render(self, name, value, attrs=None, renderer=None, **kwargs):
        input_html = super().render(name, value, attrs=None, **kwargs)
        html = Template(
            """<img src="$media$link" width="80" height="80" />""")
        img_html = mark_safe(
            html.substitute(media=settings.MEDIA_URL, link=value))
        content = mark_safe(f'{img_html}<br><br>{input_html}')
        return content


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class UserEditForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('photo',)
        widgets = {
            'photo': PictureWidget
        }


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
