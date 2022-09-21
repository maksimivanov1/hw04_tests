from django.shortcuts import render
from django.shortcuts import redirect
from .models import Post, Group
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from posts import utils

User = get_user_model()


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    page_obj = utils.paginating(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.all().order_by('-pub_date')
    page_obj = utils.paginating(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group')
    page_obj = utils.paginating(request, post_list)
    context = {
        'author': author,
        'page_obj': page_obj
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related(), id=post_id)
    context = {
        'post': post
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST)
    context = {'form': form}
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user.username)
        else:
            return render(request, 'posts/create_post.html', context)
    else:
        return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    context = {'form': form,
               'is_edit': True,
               'post_id': post_id}
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', context)
