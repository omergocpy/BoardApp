# myapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm, RatingForm
from .models import Post, Like, Rating, Comment, Poll, PollOption, PollVote
from users.models import Progress
from django.db.models import Avg, Count, Sum
from django.http import JsonResponse
from django.contrib import messages
from users.utils import update_user_points
import json

def check_for_first_post_in_category(post):
    # Kategorideki ilk gönderi bonusu
    if post.category and not Post.objects.filter(category=post.category).exclude(id=post.id).exists():
        update_user_points(post.user, 50)

@login_required(login_url='login')  
def post_list_view(request):
    user_group = request.user.group  
    posts = Post.objects.filter(approved=True, user__group=user_group).order_by('-created_at')

    for post in posts:
        # Yorum sayısı
        post.comment_count = post.comments.filter(approved=True).count()
        # İlk 3 yorum
        post.top_comments = post.comments.filter(approved=True).order_by('created_at')[:3]
        # Beğeni sayıları
        post.like_count = post.likes.filter(like_type='like').count()
        post.dislike_count = post.likes.filter(like_type='dislike').count()
        # Oylama yüzdesi
        average_rating = post.ratings.aggregate(Avg('score'))['score__avg']
        post.rating_percentage = round((average_rating / 5) * 100) if average_rating else 0

    return render(request, 'post_list.html', {'posts': posts})


@login_required(login_url='login')  
def post_create_view(request):
    progress, created = Progress.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # Seviye kontrolü: post_type'ı alıp kapalı mı diye bakarız
            post_type = form.cleaned_data.get('post_type')
            print("DEBUG => post_type is:", post_type)  # Ekledik
            if post_type == 'photo' and progress.level < 3:
                messages.error(request, "Fotoğraf paylaşmak için seviye 3 gerekiyor.")
                return redirect('post_create')
            if post_type == 'video' and progress.level < 4:
                messages.error(request, "Video paylaşmak için seviye 4 gerekiyor.")
                return redirect('post_create')
            if post_type == 'poll' and progress.level < 5:
                messages.error(request, "Anket oluşturmak için seviye 5 gerekiyor.")
                return redirect('post_create')

            post = form.save(commit=True)
            post.user = request.user
            post.save()
            
            # Kategorideki ilk paylaşım bonusu
            check_for_first_post_in_category(post)

            # Yeni gönderi puanı
            update_user_points(request.user, 30)

            return redirect('post_list')
    else:
        form = PostForm(user=request.user)

    return render(request, 'post_create.html', {
        'form': form,
        'level': progress.level
    })


@login_required(login_url='login')
def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(parent=None, approved=True)
    comment_form = CommentForm()

    media_type = None
    if post.media:
        if post.media.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            media_type = 'image'
        elif post.media.url.lower().endswith('.mp4'):
            media_type = 'video'

    like_count = post.likes.filter(like_type='like').count()
    dislike_count = post.likes.filter(like_type='dislike').count()

    rated_users = post.ratings.all()
    user_rating = post.ratings.filter(user=request.user).first()

    # Anket seçenekleri
    poll_options = []
    user_poll_vote = None  # Kullanıcının daha önceki seçeneği

    if post.post_type == 'poll' and hasattr(post, 'poll'):
        poll_options = post.poll.options.all()

        # Kullanıcının daha önce bu ankete oy verip vermediğini sorgula
        try:
            user_poll_vote = PollVote.objects.get(poll=post.poll, user=request.user)
            # user_poll_vote.option => kullanıcı hangi seçeneğe oy vermiş
        except PollVote.DoesNotExist:
            user_poll_vote = None

    if request.method == 'POST':
        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.user = request.user
                comment.save()
                # Puan eklenmesi vs.
                return redirect('post_detail', post_id=post_id)

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'media_type': media_type,
        'like_count': like_count,
        'dislike_count': dislike_count,
        'rated_users': rated_users,
        'user_rating': user_rating.score if user_rating else None,
        'poll_options': poll_options,
        # Ekledik:
        'user_poll_vote': user_poll_vote,
    })

@login_required(login_url='login')
def poll_vote_view(request, post_id):
    """Bir seçenek seçerek oy verir, tekrar oy kullanmayı engeller."""
    post = get_object_or_404(Post, id=post_id, post_type='poll')
    poll = getattr(post, 'poll', None)
    if not poll:
        return redirect('post_detail', post_id=post_id)

    option_id = request.POST.get('option_id')
    # Seçenek doğrulama
    option = get_object_or_404(PollOption, id=option_id, poll=poll)

    # 1) Kullanıcı zaten oy vermiş mi?
    existing_vote = PollVote.objects.filter(poll=poll, user=request.user).first()
    if existing_vote:
        # Zaten bu ankete oy kullanmış
        messages.error(request, "Bu ankete zaten oy kullandınız!")
        return redirect('post_detail', post_id=post_id)

    # 2) İlk kez oy veriyor => PollVote kaydı ekle
    PollVote.objects.create(
        poll=poll,
        user=request.user,
        option=option
    )

    # 3) Seçilen seçenek oy sayısını 1 arttır
    option.votes += 1
    option.save()

    # 4) Puanlama mantığı (oy veren yerine post sahibine puan verelim vs.)
    if request.user != post.user:
        update_user_points(post.user, 20)

    messages.success(request, f"{option.text} seçeneğine oy verdiniz.")
    return redirect('post_detail', post_id=post_id)


@login_required(login_url='login')
def poll_results_json(request, post_id):
    """Chart.js için JSON veri döndürür."""
    post = get_object_or_404(Post, id=post_id, post_type='poll')
    poll = getattr(post, 'poll', None)
    if not poll:
        return JsonResponse({}, status=404)

    labels = []
    data = []
    for opt in poll.options.all():
        labels.append(opt.text)
        data.append(opt.votes)

    return JsonResponse({
        'labels': labels,
        'data': data
    })


@login_required(login_url='login')
def like_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, approved=True)
    like_type = request.POST.get('like_type')  # "like" veya "dislike"

    existing_like = Like.objects.filter(post=post, user=request.user).first()
    if existing_like:
        if existing_like.like_type == like_type:
            existing_like.delete()
        else:
            existing_like.like_type = like_type
            existing_like.save()
    else:
        Like.objects.create(post=post, user=request.user, like_type=like_type)
        if request.user != post.user:
            if like_type == "like":
                update_user_points(request.user, 10)
            else:
                update_user_points(request.user, -10)
    return redirect('post_detail', post_id=post.id)


@login_required(login_url='login')
def rate_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, approved=True)
    score = request.POST.get('score')
    try:
        score = int(score)
        if score < 1 or score > 5:
            messages.error(request, "Geçersiz puan. 1 ile 5 arasında olmalı.")
            return redirect('post_detail', post_id=post.id)
    except (ValueError, TypeError):
        messages.error(request, "Geçersiz puan değeri.")
        return redirect('post_detail', post_id=post.id)

    rating, created = Rating.objects.get_or_create(post=post, user=request.user)
    rating.score = score
    rating.save()

    # Puan verildiğinde post sahibine bonus
    if created and request.user != post.user:
        update_user_points(post.user, score * 5)

    messages.success(request, f"{score} yıldız verdiniz.")
    return redirect('post_detail', post_id=post.id)


@login_required(login_url='login') 
def reply_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, approved=True)
    if request.method == 'POST':
        reply = Comment.objects.create(
            post=comment.post,
            user=request.user,
            content=request.POST.get('content'),
            parent=comment,
            approved=True  # Moderasyon yoksa doğrudan onay
        )
        update_user_points(request.user, 5)  # Yanıt için puan
        return redirect('post_detail', post_id=comment.post.id)


@login_required(login_url='login')  
def like_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, approved=True)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        if request.user in comment.dislikes.all():
            comment.dislikes.remove(request.user)
        comment.likes.add(request.user)
    return redirect('post_detail', post_id=comment.post.id)


@login_required(login_url='login') 
def dislike_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, approved=True)
    if request.user in comment.dislikes.all():
        comment.dislikes.remove(request.user)
    else:
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
        comment.dislikes.add(request.user)
    return redirect('post_detail', post_id=comment.post.id)


@login_required(login_url='login') 
def group_leaderboard_view(request):
    user_group = request.user.group
    from users.models import Progress
    leaderboard = Progress.objects.filter(user__group=user_group).order_by('-points')
    return render(request, 'group_leaderboard.html', {'leaderboard': leaderboard})
