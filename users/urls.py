from django.urls import path
from .views import login_view, register_view, profile_view, home_view, profile_detail_view, survey_view, second_survey_view, logout_view


urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('login/<str:username>/', login_view, name='login_with_username'),  
    path('home/', home_view, name='home'),
    path('profil/', profile_view, name='profil'),
    path('profil/<int:user_id>/', profile_detail_view, name='profile_detail'),
    path('logout/', logout_view, name='logout'), 
    path('survey/', survey_view, name='initial_survey'),
    path('second-survey/', second_survey_view, name='second_survey'),
]
