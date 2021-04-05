from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse

from posts.models import Profile

from .forms import CreationForm

User = get_user_model()


from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Topic, Message

User = get_user_model()


@login_required
def topics(request):
    pm_topics = Topic.objects.filter(sender=request.user)
    return render(
        request,
        'private_messages/topics.html',
        {'pm_topics': pm_topics})


@login_required
def topic_new(request):
    pass


@login_required
def topic_read(request, topic_id):
    pass


@login_required
def topic_delete(request):
    pass


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/signup.html'

    def form_valid(self, form):
        """
        автоматический вход после регистрации пользователя
        """
        form.save()
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'])
        login(self.request, user)
        return HttpResponseRedirect(reverse('index'))


@receiver(post_save, sender=User)
def save_or_create_profile(sender, instance, created, **kwargs):
    """
    автоматическое создание профиля для существующих и новых пользователей
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        try:
            instance.profile.save()
        except ObjectDoesNotExist:
            Profile.objects.create(user=instance)
