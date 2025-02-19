from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm, CommentForm
from django.db.models import Count, Q, Avg, Sum
from .models import Post, Like, Rating, Comment
from users.models import Progress
from django.http import HttpResponse
from django.contrib.auth import logout
from users.utils import update_user_points
from django.contrib.auth.decorators import login_required
from django.contrib import messages



def check_for_first_post_in_category(post):
    if not Post.objects.filter(category=post.category).exists():
        print(f"İlk paylaşım bonusu veriliyor: {post.user.username}")
        update_user_points(post.user, 50) 



def check_for_daily_top_post():
    from datetime import datetime
    top_post = Post.objects.filter(created_at__date=datetime.today()).annotate(interactions=Count('likes') + Count('comments')).order_by('-interactions').first()
    if top_post:
        update_user_points(top_post.user, 50)  # Dünün öne çıkan paylaşımı sonrası puan güncelleme


@login_required(login_url='login')  
def post_list_view(request):
    user_group = request.user.group  # Kullanıcının grubu
    posts = Post.objects.filter(approved=True, user__group=user_group).order_by('-created_at')

    for post in posts:
        # Yorum sayısı
        post.comment_count = post.comments.filter(approved=True).count()

        # İlk 3 yorum
        post.top_comments = post.comments.filter(approved=True).order_by('created_at')[:3]

        # Beğeni ve beğenmeme sayısı
        post.like_count = post.likes.filter(like_type='like').count()
        post.dislike_count = post.likes.filter(like_type='dislike').count()

        # Oylama yüzdesi
        average_rating = post.ratings.aggregate(Avg('score'))['score__avg']
        if average_rating:
            post.rating_percentage = round((average_rating / 5) * 100)
        else:
            post.rating_percentage = 0

    return render(request, 'post_list.html', {'posts': posts})



@login_required(login_url='login')  
def post_create_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    progress = Progress.objects.get_or_create(user=request.user)[0]
    form = PostForm(request.POST or None, request.FILES or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.user = request.user
        post.save()

        # Kategorideki ilk gönderiyi kontrol et
        check_for_first_post_in_category(post)

        # Kullanıcıya puan ekle
        update_user_points(request.user, 30) 
        return redirect('post_list')

    return render(request, 'post_create.html', {
        'form': form,
        'level': progress.level
    })


@login_required(login_url='login')
def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(parent=None, approved=True)  # Only approved comments
    comment_form = CommentForm()

    media_type = None
    if post.media:
        if post.media.url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            media_type = 'image'
        elif post.media.url.endswith('.mp4'):
            media_type = 'video'

    # Calculate like and dislike counts
    like_count = post.likes.filter(like_type='like').count()
    dislike_count = post.likes.filter(like_type='dislike').count()

    # Get users who rated the post and the current user's rating
    rated_users = post.ratings.all()
    user_rating = post.ratings.filter(user=request.user).first()

    if request.method == 'POST':
        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.user = request.user
                comment.save()
                
                if created and request.user != post.user:
                    update_user_points(post.user, 10)

                return redirect('post_detail', post_id=post_id)

        if 'score' in request.POST:
            score = int(request.POST.get('score', 0))
            rating, created = Rating.objects.get_or_create(post=post, user=request.user)
            rating.score = score
            rating.save()

            if created and request.user != post.user:
                update_user_points(post.user, score * 5)

            return redirect('post_detail', post_id=post_id)




    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'media_type': media_type,
        'like_count': like_count,
        'dislike_count': dislike_count,
        'rated_users': rated_users,  # Oylama yapan kullanıcılar
        'user_rating': user_rating.score if user_rating else None,  # Kullanıcının oyu
    })

@login_required(login_url='login')
def like_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, approved=True)
    like_type = request.POST.get('like_type')  # "like" veya "dislike"

    existing_like = Like.objects.filter(post=post, user=request.user).first()

    if existing_like:
        # Eğer mevcut bir kayıt varsa iki ihtimal:
        # 1) Aynı türse => kullanıcı beğenisini kaldırıyor
        # 2) Farklı türse => kullanıcı 'like'tan 'dislike'a veya tam tersi geçiyor
        if existing_like.like_type == like_type:
            # 1) Tamamen kaldır
            existing_like.delete()
        else:
            # 2) Tür değişikliği
            existing_like.like_type = like_type
            existing_like.save()
        # NOT: Hiçbir puan değişikliği yapmayın.
    else:
        # Hiç yok => yeni bir beğeni veya beğenmeme ekleniyor
        Like.objects.create(post=post, user=request.user, like_type=like_type)

        # Kendi paylaşımından puan almaması için kontrol:
        if request.user != post.user:
            if like_type == "like":
                update_user_points(request.user, 10)  # Yeni like
            else:
                update_user_points(request.user, -10)  # Yeni dislike

    return redirect('post_detail', post_id=post.id)


@login_required(login_url='login')
def rate_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, approved=True)
    score = request.POST.get('score')

    try:
        score = int(score)
        if score < 1 or score > 5:
            messages.error(request, "Geçersiz puan. Puan 1 ile 5 arasında olmalıdır.")
            return redirect('post_detail', post_id=post.id)
    except (ValueError, TypeError):
        messages.error(request, "Geçersiz puan değeri.")
        return redirect('post_detail', post_id=post.id)

    rating, created = Rating.objects.get_or_create(post=post, user=request.user)
    rating.score = score
    rating.save()

    # Puan ekleme işlemini oy veren yerine post sahibine yapalım
    if created:
        update_user_points(post.user, score * 5)

    messages.success(request, f"{score} yıldız verdiniz. Teşekkürler!")
    return redirect('post_detail', post_id=post.id)



@login_required(login_url='login') 
def reply_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, approved=True)
    if request.method == 'POST':
        reply = Comment.objects.create(
            post=comment.post,
            user=request.user,
            content=request.POST.get('content'),
            parent=comment
        )
        return redirect('post_detail', post_id=comment.post.id)


@login_required(login_url='login')  
def like_comment_view(request, comment_id):
    try:
        comment = get_object_or_404(Comment, id=comment_id)
    except Comment.DoesNotExist:
        return HttpResponse("Yorum bulunamadı veya onaylanmadı.", status=404)

    # Beğenmeler arasında kullanıcı varsa kaldır, aksi halde ekle
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        # Kullanıcı daha önce beğenmeme yaptıysa, onu kaldır
        if request.user in comment.dislikes.all():
            comment.dislikes.remove(request.user)
        comment.likes.add(request.user)  # Beğenme ekle

    return redirect('post_detail', post_id=comment.post.id)


@login_required(login_url='login') 
def dislike_comment_view(request, comment_id):
    try:
        comment = get_object_or_404(Comment, id=comment_id)
    except Comment.DoesNotExist:
        return HttpResponse("Yorum bulunamadı veya onaylanmadı.", status=404)

    # Beğenmeme listesi arasında kullanıcı varsa kaldır, aksi halde ekle
    if request.user in comment.dislikes.all():
        comment.dislikes.remove(request.user)
    else:
        # Kullanıcı daha önce beğenme yaptıysa, onu kaldır
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
        comment.dislikes.add(request.user)  # Beğenmeme ekle

    return redirect('post_detail', post_id=comment.post.id)



@login_required(login_url='login') 
def logout_view(request):
    logout(request)
    return redirect('post_list')  


@login_required(login_url='login') 
def group_leaderboard_view(request):
    user_group = request.user.group
    leaderboard = Progress.objects.filter(user__group=user_group).order_by('-points')
    return render(request, 'group_leaderboard.html', {'leaderboard': leaderboard})


def update_group_progress(user, points):
    user.progress.points += points
    user.progress.save()

    # Grup toplam puanını güncelle
    user_group = user.group
    group_total_points = Progress.objects.filter(user__group=user_group).aggregate(Sum('points'))['points__sum']
    if group_total_points >= 500:
        # Grubun seviyesi yükseltiliyor
        user_group.level += 1
        user_group.save()


