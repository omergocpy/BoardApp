import random
from django.shortcuts import render, redirect,get_object_or_404
from .forms import RegisterForm
from .models import Progress, Group, CustomUser
from django.db.models import Sum
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from posts.models import Comment, Post
from django.core.paginator import Paginator
from .models import InitialSurvey, UserSurveyResponse, SurveyCompletion, LIKERT_CHOICES
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import logout
from .utils import get_group_features,  get_user_ranking_info, assign_group_to_user_sequentially

@login_required(login_url='login')
def second_survey_view(request):
    completion, created = SurveyCompletion.objects.get_or_create(user=request.user)
    
    if not completion.completed:
        messages.info(request, "Önce ilk anketi tamamlamanız gerekiyor.")
        return redirect('initial_survey')
    
    if completion.second_survey_completed:
        messages.info(request, "Anketi daha önce tamamladınız.")
        return redirect('home')
    
    if not completion.is_second_survey_due():
        from django.utils import timezone
        import datetime
        
        if completion.completed_at:
            seven_days_later = completion.completed_at + datetime.timedelta(days=7)
            days_left = (seven_days_later - timezone.now()).days
            
            if days_left > 0:
                messages.info(request, f"Takip anketi için henüz {days_left} gün kaldı.")
            else:
                # Saatleri hesapla
                hours_left = int((seven_days_later - timezone.now()).total_seconds() / 3600)
                if hours_left > 0:
                    messages.info(request, f"Takip anketi için henüz {hours_left} saat kaldı.")
                else:
                    messages.info(request, "Takip anketi yakında aktif olacak.")
        
        return redirect('home')

@login_required(login_url='login')
def second_survey_view(request):
    completion, created = SurveyCompletion.objects.get_or_create(user=request.user)
    
    if not completion.completed:
        messages.info(request, "Önce ilk anketi tamamlamanız gerekiyor.")
        return redirect('initial_survey')
    
    if completion.second_survey_completed:
        messages.info(request, "İkinci anketi daha önce tamamladınız.")
        return redirect('home')
    
    if not completion.is_second_survey_due():
        from django.utils import timezone
        import datetime
        
        if completion.completed_at:
            fourteen_days_later = completion.completed_at + datetime.timedelta(days=14)
            days_left = (fourteen_days_later - timezone.now()).days
            
            if days_left > 0:
                messages.info(request, f"İkinci anket için henüz {days_left} gün kaldı.")
            else:
                # Saatleri hesapla
                hours_left = int((fourteen_days_later - timezone.now()).total_seconds() / 3600)
                if hours_left > 0:
                    messages.info(request, f"İkinci anket için henüz {hours_left} saat kaldı.")
                else:
                    messages.info(request, "İkinci anket yakında aktif olacak.")
        
        return redirect('home')
    
    questions = InitialSurvey.objects.filter(is_active=True)
    
    if not questions.exists():
        messages.error(request, "Şu anda aktif anket sorusu bulunmuyor.")
        return redirect('home')
    
    if request.method == 'POST':
        all_answered = True
        answers = {}
        
        for question in questions:
            field_name = f'question_{question.id}'
            if field_name in request.POST and request.POST[field_name]:
                answers[field_name] = int(request.POST[field_name])
            else:
                all_answered = False
        
        if all_answered:
            for question in questions:
                field_name = f'question_{question.id}'
                answer_value = answers[field_name]
                
                UserSurveyResponse.objects.update_or_create(
                    user=request.user,
                    question=question,
                    is_second_response=True,  
                    defaults={'answer': answer_value}
                )
            
            completion.second_survey_completed = True
            completion.second_survey_completed_at = timezone.now()
            completion.save()
            
            messages.success(request, "İkinci anket başarıyla tamamlandı. Teşekkür ederiz!")
            return redirect('home')
        else:
            messages.error(request, "Lütfen tüm soruları cevaplayınız.")
    
    user_responses = {}
    first_responses = UserSurveyResponse.objects.filter(
        user=request.user,
        question__in=questions,
        is_second_response=False
    )
    
    for response in first_responses:
        user_responses[response.question.id] = response.answer
    
    return render(request, 'second_survey_form.html', {
        'questions': questions,
        'LIKERT_CHOICES': LIKERT_CHOICES,
        'user_responses': user_responses,
        'is_second_survey': True
    })
    
@login_required(login_url='login')
def survey_view(request):
    # Kullanıcı anketi daha önce tamamladıysa, ana sayfaya yönlendir
    completion, created = SurveyCompletion.objects.get_or_create(user=request.user)
    if completion.completed:
        messages.info(request, "Bu anketi daha önce tamamladınız.")
        return redirect('home')
    
    # Aktif soruları al
    questions = InitialSurvey.objects.filter(is_active=True)
    
    # Soru yoksa anket tamamlanmış kabul et
    if not questions.exists():
        completion.completed = True
        completion.completed_at = timezone.now()
        completion.save()
        messages.success(request, "Şu anda aktif anket bulunmadığından, anket tamamlandı kabul edildi.")
        return redirect('home')
    
    if request.method == 'POST':
        # Formdan verileri al
        all_answered = True
        answers = {}
        
        for question in questions:
            field_name = f'question_{question.id}'
            if field_name in request.POST and request.POST[field_name]:
                answers[field_name] = int(request.POST[field_name])
            else:
                all_answered = False
        
        if all_answered:
            # Cevapları kaydet
            for question in questions:
                field_name = f'question_{question.id}'
                answer_value = answers[field_name]
                
                UserSurveyResponse.objects.update_or_create(
                    user=request.user,
                    question=question,
                    defaults={'answer': answer_value}
                )
            
            # Anketi tamamla
            completion.completed = True
            completion.completed_at = timezone.now()
            completion.save()
            
            messages.success(request, "Anket başarıyla tamamlandı. Teşekkür ederiz!")
            return redirect('home')
        else:
            messages.error(request, "Lütfen tüm soruları cevaplayınız.")
    
    # Kullanıcının daha önce verdiği cevapları yükle
    user_responses = {}
    existing_responses = UserSurveyResponse.objects.filter(
        user=request.user,
        question__in=questions
    )
    
    for response in existing_responses:
        user_responses[response.question.id] = response.answer
    
    return render(request, 'survey_form.html', {
        'questions': questions,
        'LIKERT_CHOICES': LIKERT_CHOICES,
        'user_responses': user_responses
    })
    
    
def login_view(request, username=None):
    if request.method == 'POST':
        username = request.POST['username']  
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                survey_completion = SurveyCompletion.objects.get(user=user)
                if not survey_completion.completed:
                    return redirect('initial_survey')
            except SurveyCompletion.DoesNotExist:
                SurveyCompletion.objects.create(user=user, completed=False)
                return redirect('initial_survey')
                
            return redirect('home')  
        else:
            messages.error(request, 'Geçersiz kullanıcı ID veya şifre.')
    else:
        if username:
            return render(request, 'login.html', {'username': username})
    return render(request, 'login.html')


def generate_random_id():
    return str(random.randint(1000, 9999))


def generate_unique_numeric_username():
    while True:
        username_candidate = str(random.randint(1000, 9999))
        if not CustomUser.objects.filter(username=username_candidate).exists():
            return username_candidate
        
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
            user.username = generate_unique_numeric_username() 
            user.save()
            
            assign_group_to_user_sequentially(user)
            
            # Progress oluştur
            Progress.objects.create(user=user)
            
            # Anket tamamlama kaydı oluştur
            SurveyCompletion.objects.create(user=user, completed=False)

            messages.success(request, f"Tebrikler! Kullanıcı kaydınız oluşturulmuştur. Bundan sonra kullanıcı adınız {user.username} dir. "
                                      f"Lütfen kullanıcı adınızı ve şifrenizi unutmamak için hemen bir kağıda not alın, "
                                      f"bundan sonra bu kullanıcı adı ve belirlediğiniz şifre ile giriş yapabilirisiniz.")

            # Kullanıcıyı otomatik giriş yap ve ankete yönlendir
            login(request, user)
            return redirect('initial_survey')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})

@login_required(login_url='login')  
def home_view(request):
    # İkinci anket hatırlatması kontrolü
    try:
        survey_completion = SurveyCompletion.objects.get(user=request.user)
        if survey_completion.completed and not survey_completion.second_survey_completed:
            if survey_completion.is_second_survey_due():
                messages.info(request, "Takip anketi için zamanınız geldi. Lütfen anketi tamamlayın.")
                # Anket butonunu ekle
                messages.info(request, '<a href="{% url "second_survey" %}" class="btn btn-success">Anketi Tamamla</a>', extra_tags='safe')
    except SurveyCompletion.DoesNotExist:
        pass
    
    # Ana sayfaya yönlendir
    return redirect('post_list')


@login_required(login_url='login')  
def profile_view(request):
    user = request.user
    progress = getattr(user, 'progress_instance', None)
    
    if progress is None:
        level = 1
        progress_percentage = 0
        points = 0
        progress_text = "Seviye 1 (0/100)"
        group_progress = 0
        group_level = 1
        user_ranking_in_group = "Yok"
        feature_details = []

    else:
        level = progress.level
        progress_percentage = progress.get_progress_percentage()
        points = progress.points
        progress_text = progress.get_level_progress_text()
        group_progress = Progress.objects.filter(user__group=user.group).aggregate(Sum('points'))['points__sum'] or 0
        group_level = user.group.level
        user_ranking_in_group = Progress.objects.filter(user__group=user.group).order_by('-points').filter(points__gte=progress.points).count()
        feature_details = progress.get_feature_details()

    ranking_info = get_user_ranking_info(user)

    return render(request, 'profil.html', {
        'user': user,
        'level': level,
        'progress': progress_percentage,
        'progress_text': progress_text,  
        'points': points,
        'group_progress': group_progress,
        'group_level': group_level,
        'user_ranking_in_group': user_ranking_in_group,
        'ranking_info': ranking_info,
        'feature_details': feature_details
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
    
    group_name = user.group.name if user.group else None
    group_features = get_group_features(group_name)
    
    level = progress.level if progress else 1
    points = progress.points if progress else 0
    progress_percentage = progress.get_progress_percentage() if progress else 0
    progress_text = progress.get_level_progress_text() if progress else "Seviye 1 (0/100)"
    
    ranking_info = get_user_ranking_info(user)
    
    user_posts = Post.objects.filter(user=user, approved=True).order_by('-created_at')
    
    for post in user_posts:
        post.like_count = post.likes.filter(like_type='like').count()
        post.dislike_count = post.likes.filter(like_type='dislike').count()
        post.comment_count = post.comments.filter(approved=True).count()
    
    post_page = request.GET.get('page', 1)
    post_paginator = Paginator(user_posts, 5)  
    
    user_comments = Comment.objects.filter(user=user, approved=True).order_by('-created_at')
    
    comment_details = []
    for comment in user_comments:
        comment_details.append({
            'comment': comment,
            'post_title': comment.post.content[:50] + '...' if len(comment.post.content) > 50 else comment.post.content,
            'post_id': comment.post.id,
            'post_user': comment.post.user
        })
    
    comment_page = request.GET.get('comment_page', 1)
    comment_paginator = Paginator(comment_details, 5) 
    
    feature_details = []
    if progress:
        feature_details = progress.get_feature_details()
    
    return render(request, 'profile_detail.html', {
        'user_detail': user,
        'level': level,
        'points': points,
        'progress_percentage': progress_percentage,
        'progress_text': progress_text,
        'ranking_info': ranking_info,
        'user_posts': post_paginator.get_page(post_page),
        'feature_details': feature_details,
        'user_comment_details': comment_paginator.get_page(comment_page),
        'group_features': group_features,
        'group_name': group_name
    })
    
def logout_view(request):
    logout(request)
    messages.success(request, "Başarıyla çıkış yapıldı.")
    return redirect('login')