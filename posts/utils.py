from .models import Post
from datetime import datetime
from users.utils import update_user_points
from django.db.models import Count


def check_for_first_post_in_category(post):
    if not Post.objects.filter(category=post.category).exists():
        update_user_points(post.user, 50)  # Kategoride ilk paylaşım bonusu.

def check_for_daily_top_post():
    top_post = Post.objects.filter(created_at__date=datetime.today()).annotate(interactions=Count('likes') + Count('comments')).order_by('-interactions').first()
    if top_post:
        update_user_points(top_post.user, 50)  # Dünün öne çıkan paylaşımı bonusu.
