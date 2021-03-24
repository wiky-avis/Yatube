from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render)

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    post_list = get_list_or_404(Post)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'index.html', {
            'page': page,
            'paginator': paginator,
            'is_active': True})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'group.html', {
            'group': group,
            'page': page,
            'paginator': paginator,
            'is_active': True})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'posts/new_post.html', {'form': form})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(instance=None)
    comments = post.comments.all()
    return render(
        request, 'posts/post.html', {
            'profile': post.author,
            'post': post,
            'count': post.author.posts.count(),
            'form': form,
            'comments': comments})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect(
            'post', post_id=post.id, username=post.author.username)
    return render(
        request, 'post.html', {
            'form': form,
            'post': post,
            'comments': comments})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user != post.author:
        return redirect(
            'post', post_id=post.id, username=post.author.username)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect(
            'post', post_id=post.id, username=post.author.username)
    return render(
        request, 'posts/new_post.html', {'form': form, 'post': post})


@login_required
def post_delete(request, username, post_id):
    post = get_object_or_404(
        Post, author__username=username, id=post_id)
    post.delete()
    return redirect('profile', username=post.author.username)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = profile.posts.all()
    count = posts.count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'posts/profile.html', {
            'page': page,
            'count': count,
            'profile': profile,
            'is_active': True,
            'follower': profile.follower.count(),
            'following': profile.following.count()})


@login_required
def follow_index(request):
    posts = Post.objects.select_related('author').filter(
        author__following__user=request.user).all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/follow.html',
        {
            'paginator': paginator,
            'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get(user=request.user, author=author).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
