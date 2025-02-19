from django.urls import path
from .views import login_view, register_view, profile_view, home_view, profile_detail_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('login/<str:username>/', login_view, name='login_with_username'),  
    path('home/', home_view, name='home'),
    path('profil/', profile_view, name='profil'),
    path('profil/<int:user_id>/', profile_detail_view, name='profile_detail'),

    ]
