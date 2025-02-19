from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Board Yönetimi"
admin.site.site_title = "Board Yönetim Paneli"
admin.site.index_title = "Hoşgeldiniz"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), 
    path('', include('users.urls')), 
    path('', include('posts.urls')), 
    path('support/', include('support.urls')), 
    path('', include('scoreboards.urls')), 

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)