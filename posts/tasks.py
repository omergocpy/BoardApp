from celery import shared_task
from .models import Post
from django.db.models import Count
from datetime import datetime
from users.utils import update_user_points

@shared_task
def check_for_daily_top_post():
    top_post = Post.objects.filter(created_at__date=datetime.today()).annotate(interactions=Count('likes') + Count('comments')).order_by('-interactions').first()
    if top_post:
        update_user_points(top_post.user, 50)  # Dünün öne çıkan paylaşımı sonrası puan güncelleme
