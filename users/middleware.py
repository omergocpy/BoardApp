from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import UserSession
from .models import SurveyCompletion

class SurveyCompletionMiddleware:
    """
    Kullanıcı anketi tamamlamamışsa, anket sayfasına yönlendirir.
    İzin verilen URL'ler: login, logout, register, admin ve anket sayfası
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # İstek işlenmeden önce kod
        
        # Admin, login, logout, register ve anket sayfalarını her zaman erişilebilir kıl
        allowed_urls = [
            'login', 'logout', 'register', 'initial_survey', 'login_with_username',
            'admin:index', 'admin:login'
        ]
        
        # Statik dosyalar ve admin için izin ver
        if request.path.startswith('/static/') or request.path.startswith('/media/') or \
           request.path.startswith('/admin/'):
            return self.get_response(request)
            
        # Kullanıcı giriş yapmışsa ve izin verilen URL'lerden birine gitmeye çalışmıyorsa
        if request.user.is_authenticated and not any(request.resolver_match.url_name == url for url in allowed_urls):
            try:
                # Admin kullanıcıları her zaman geçebilir
                if request.user.is_staff or request.user.is_superuser:
                    return self.get_response(request)
                    
                # Kullanıcının anket tamamlama durumunu kontrol et
                completion = SurveyCompletion.objects.get(user=request.user)
                
                # Anket tamamlanmamışsa, anket sayfasına yönlendir
                if not completion.completed:
                    if request.resolver_match.url_name != 'initial_survey':
                        messages.warning(request, "Uygulamaya devam etmek için lütfen anketi tamamlayın.")
                        return redirect('initial_survey')
                
            except SurveyCompletion.DoesNotExist:
                # Anket tamamlama kaydı yoksa oluştur
                SurveyCompletion.objects.create(user=request.user, completed=False)
                if request.resolver_match.url_name != 'initial_survey':
                    return redirect('initial_survey')
        
        # İstek işlendikten sonra dönecek yanıt
        response = self.get_response(request)
        return response
    
    
class UserSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # İstek işlenmeden önce
        if request.user.is_authenticated:
            # Kullanıcının aktif bir oturumu var mı kontrol et
            session_key = request.session.session_key
            if not UserSession.objects.filter(user=request.user, session_key=session_key, logout_time__isnull=True).exists():
                # Yeni oturum oluştur
                UserSession.objects.create(
                    user=request.user,
                    session_key=session_key,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
        
        response = self.get_response(request)
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# Sinyaller ile giriş/çıkış takibi
@receiver(user_logged_in)
def on_user_login(sender, request, user, **kwargs):
    # Giriş sinyali alındığında yeni oturum oluştur
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key
    
    # IP ve user agent bilgilerini al
    ip_address = None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
        
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Yeni oturum oluştur
    UserSession.objects.create(
        user=user,
        session_key=session_key,
        ip_address=ip_address,
        user_agent=user_agent
    )

@receiver(user_logged_out)
def on_user_logout(sender, request, user, **kwargs):
    # Çıkış sinyali alındığında oturumu kapat
    if user:
        session_key = request.session.session_key
        try:
            user_session = UserSession.objects.get(
                user=user,
                session_key=session_key,
                logout_time__isnull=True
            )
            user_session.logout_time = timezone.now()
            user_session.save()
        except UserSession.DoesNotExist:
            pass  # Oturum bulunamadı, muhtemelen zaten kapanmış