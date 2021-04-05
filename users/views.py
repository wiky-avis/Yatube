from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.http import HttpResponseRedirect
from django.urls import reverse

from posts.models import Profile

from .forms import CreationForm, NewTopicForm, MessageSendForm

from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from .models import Topic, Message
from datetime import datetime

User = get_user_model()


@login_required
def topics(request):
    pm_topics = Topic.objects.by_user(request.user)
    user = request.user
    profile = get_object_or_404(User, id=request.user.id)
    photo = get_object_or_404(Profile, user=profile)
    count_unread_messages = user.sender_messages.filter(read_at__exact=None).count()
    last_unread_message = user.sender_messages.order_by('-sent_at').filter(read_at__exact=None)

    return render(
        request,
        'private_messages/topics.html',
        {
            'pm_topics': pm_topics,
            'user': user,
            'count_unread_messages': count_unread_messages,
            'last_unread_message': last_unread_message,
            'profile': profile,
            'photo': photo})


@login_required
def topic_new(request, user_id):
    recipient = get_object_or_404(User, id=user_id)
    photo = get_object_or_404(Profile, user=recipient)
    count_unread_messages = recipient.sender_messages.filter(read_at__exact=None).count()

    form = NewTopicForm(request.POST or None,)
    if form.is_valid():
        message = form.save(commit=False)

        topic = Topic(sender=request.user)
        topic.recipient = recipient
        topic.subject = form.cleaned_data['subject']
        topic.last_sent_at = datetime.now()
        topic.save()

        message.topic = topic
        message.sender = request.user
        message.save()

        return redirect(reverse('private_messages'))
    return render(request, 'private_messages/topic_new.html', {'pm_form': form, 'recipient': recipient, 'profile': recipient, 'photo': photo, 'count_unread_messages': count_unread_messages})


@login_required
def topic_read(request, topic_id):
    topic = get_object_or_404(Topic.objects.by_user(request.user), id=topic_id)
    recipient = get_object_or_404(User, id=topic.recipient.id)
    messages_all = topic.topic_messages.all()
    profile = get_object_or_404(User, id=request.user.id)
    photo = get_object_or_404(Profile, user=profile)
    count_unread_messages = messages_all.count()

    form = MessageSendForm(request.POST or None, instance=topic)
    if form.is_valid():
        message = form.save(commit=False)
        message.topic = topic
        message.recipient = recipient
        message.sender = request.user
        message.save()

        topic.last_sent_at = message.sent_at
        topic.subject = topic.subject
        topic.save()

        return redirect(reverse('private_messages'))

    # помечаем сообщения как прочитанные
    Message.objects.mark_read(request.user, topic)

    return render(
        request,
        'private_messages/topic_read.html',
        {
            'pm_topic': topic,
            'pm_form': form,
            'messages_all': messages_all,
            'recipient': recipient,
            'profile': profile,
            'photo': photo,
            'count_unread_messages': count_unread_messages})


@login_required
def topic_delete(request):
    topics = []
    if request.method == 'POST':
        topics = request.POST.getlist('topic[]')
    elif 'topic_id' in request:
        topics.append(request.GET['topic_id'])

    for topic_id in topics:
        try:
            topic = Topic.objects.by_user(request.user).get(pk=topic_id)
            topic.delete()
        except Topic.DoesNotExist:
            pass

    return redirect(reverse('private_messages'))


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
        return redirect(reverse('index'))


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
