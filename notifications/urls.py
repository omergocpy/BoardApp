from django.urls import path
from . import views

urlpatterns = [
    path('bildirimler/', views.notifications_list, name='notifications_list'),
    path('bildirim/<int:notification_id>/okundu/', views.mark_notification_read, name='mark_notification_read'),
    path('bildirimler/tumunu-okundu-isaretle/', views.mark_all_read, name='mark_all_read'),
    path('bildirimler/sayi/', views.get_notifications_count, name='get_notifications_count'),
]