from django.shortcuts import redirect
from django.contrib import messages

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