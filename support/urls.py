from django.urls import path
from . import views

urlpatterns = [
    path('destek-talepleri/', views.support_request_list, name='support_request_list'),
    path('yeni-destek-talebi/', views.support_request_create, name='support_request_create'),
    path('destek-talebi/<int:pk>/', views.support_request_detail, name='support_request_detail'),
]