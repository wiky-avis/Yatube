from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
# from string import Template
# from django.utils.safestring import mark_safe
# from django.conf import settings

from posts.models import Profile

User = get_user_model()


# class PictureWidget(forms.widgets.Widget):
#     def render(self, name, value, attrs=None, renderer=None):
#         html = Template("""<img src="$media$link" width="50" height="60" />""")
#         return mark_safe(html.substitute(media=settings.MEDIA_URL, link=value))


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
        # widgets = {
        #     'photo': PictureWidget
        # }
