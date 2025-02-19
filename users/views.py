import random
import string
from django.shortcuts import render, redirect,get_object_or_404
from .forms import RegisterForm
from .models import Progress, Group, CustomUser
from django.db.models import Sum
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from posts.models import Comment, Post
from django.core.paginator import Paginator


def login_view(request, username=None):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  
        else:
            messages.error(request, 'Geçersiz kullanıcı ID veya şifre.')
    else:
        if username:
            return render(request, 'login.html', {'username': username})
    return render(request, 'login.html')


def generate_random_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


def assign_group_to_user(user):
    groups = Group.objects.all()
    assigned_group = random.choice(groups)  
    user.group = assigned_group
    user.save()


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = generate_random_id()
            user.save()
            assign_group_to_user(user)  
            Progress.objects.create(user=user)  
            return redirect('login_with_username', username=user.username)
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


@login_required(login_url='login')  
def home_view(request):
    return render(request, 'home.html')


@login_required(login_url='login')  
def profile_view(request):
    user = request.user
    progress = getattr(user, 'progress_instance', None)
    
    if progress is None:
        level = 1
        progress_percentage = 0
        points = 0
        group_progress = 0
        group_level = 1
        user_ranking_in_group = "Yok"
    else:
        level = progress.level
        progress_percentage = progress.get_progress_percentage()
        points = progress.points  # Kullanıcı puanları burada ekleniyor
        group_progress = Progress.objects.filter(user__group=user.group).aggregate(Sum('points'))['points__sum'] or 0
        group_level = user.group.level
        user_ranking_in_group = Progress.objects.filter(user__group=user.group).order_by('-points').filter(user=user).count()

    return render(request, 'profil.html', {
        'user': user,
        'level': level,
        'progress': progress_percentage,
        'points': points,  # Puanları şablona gönderiyoruz
        'group_progress': group_progress,
        'group_level': group_level,
        'user_ranking_in_group': user_ranking_in_group,
    })



@login_required(login_url='login')  
def post_add_view(request):
    if request.method == 'POST':
        pass

    return render(request, 'post-add.html')

@login_required
def profile_detail_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    progress = getattr(user, 'progress_instance', None)
    
    level = progress.level if progress else 1
    points = progress.points if progress else 0
    progress_percentage = progress.get_progress_percentage() if progress else 0

    # Kullanıcı paylaşımları için sayfalama
    user_posts = Post.objects.filter(user=user).order_by('-created_at')
    post_page = request.GET.get('page', 1)
    post_paginator = Paginator(user_posts, 5)  # Her sayfada 5 paylaşım

    # Kullanıcı yorumları için sayfalama
    user_comments = Comment.objects.filter(user=user).order_by('-created_at')
    comment_page = request.GET.get('comment_page', 1)
    comment_paginator = Paginator(user_comments, 5)  # Her sayfada 5 yorum

    return render(request, 'profile_detail.html', {
        'user_detail': user,
        'level': level,
        'points': points,
        'progress_percentage': progress_percentage,
        'user_posts': post_paginator.get_page(post_page),
        'user_comments': comment_paginator.get_page(comment_page),
    })