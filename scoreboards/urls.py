from django.urls import path
from . import views

urlpatterns = [
    path('scoreboard/<int:competition_id>/', views.scoreboard_view, name='scoreboard_list'),
]
