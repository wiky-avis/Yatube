from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from posts.models import Profile

from .forms import MessageSendForm, NewTopicForm
from .models import Message, Topic

User = get_user_model()


@login_required
def topics(request):
    profile = get_object_or_404(User, id=request.user.id)
    pm_topics = Topic.objects.by_user(profile)
    photo = get_object_or_404(Profile, user=profile)

    return render(
        request,
        'private_messages/topics.html',
        {
            'pm_topics': pm_topics,
            'profile': profile,
            'photo': photo})


@login_required
def topic_new(request, user_id):
    recipient = get_object_or_404(User, id=user_id)
    photo = get_object_or_404(Profile, user=recipient)
    count_message = Topic.objects.by_user(user=recipient).count()
    count_unread = Message.objects.count_unread(user=recipient)

    form = NewTopicForm(request.POST or None)
    if form.is_valid():
        message = form.save(commit=False)

        topic = Topic(sender=request.user)
        topic.recipient = recipient

        topic.last_sent_at = datetime.now()
        topic.subject = form.cleaned_data['subject']
        topic.save()

        message.topic = topic
        message.sender = request.user
        message.save()

        return redirect(reverse('private_messages'))
    return render(
        request,
        'private_messages/topic_new.html',
        {
            'pm_form': form,
            'recipient': recipient,
            'profile': recipient,
            'photo': photo,
            'count_unread': count_unread,
            'count_message': count_message})


@login_required
def answer_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    recipient = get_object_or_404(User, id=topic.sender.id)

    form = NewTopicForm(request.POST or None, instance=topic)
    if form.is_valid():
        message = form.save(commit=False)

        topic.recipient = recipient
        topic.last_sent_at = datetime.now()
        topic.subject = topic.subject
        topic.save()

        message.topic = topic
        message.sender = request.user
        message.save()

        return redirect(reverse('private_messages'))
    return render(
        request,
        'private_messages/topic_read.html',
        {
            'pm_form': form,
            'recipient': recipient,
            'profile': recipient})


@login_required
def topic_read(request, topic_id):
    topic = get_object_or_404(Topic.objects.by_user(request.user), id=topic_id)
    recipient = get_object_or_404(User, id=topic.recipient.id)
    messages_all = topic.topic_messages.all()
    profile = get_object_or_404(User, id=request.user.id)
    photo = get_object_or_404(Profile, user=profile)

    form = MessageSendForm(request.POST or None, instance=topic)

    # ???????????????? ?????????????????? ?????? ??????????????????????
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
            'topic': topic})


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
