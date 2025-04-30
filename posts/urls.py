# myapp/urls.py
from django.urls import path
from .views import (
    post_list_view,
    post_create_view,
    post_detail_view,
    like_post_view,
    rate_post_view,
    like_comment_view,
    reply_comment_view,
    dislike_comment_view,
    poll_vote_view,
    poll_results_json,
    group_leaderboard_view,
    ajax_like_post_view
)

urlpatterns = [
    # Gönderiler
    path('', post_list_view, name='post_list'),
    path('create/', post_create_view, name='post_create'),
    path('post/<int:post_id>/', post_detail_view, name='post_detail'),
    path('post/<int:post_id>/like/', like_post_view, name='like_post'),
    path('post/<int:post_id>/rate/', rate_post_view, name='rate_post'),

    # Yorumlar
    path('comment/<int:comment_id>/like/', like_comment_view, name='like_comment'),
    path('comment/<int:comment_id>/dislike/', dislike_comment_view, name='dislike_comment'),
    path('comment/<int:comment_id>/reply/', reply_comment_view, name='reply_comment'),



    # --- Ek Özellikler (Anketler, Leaderboard) ---
    # Anket Oylama
    path('post/<int:post_id>/poll_vote/', poll_vote_view, name='poll_vote'),
    path('post/<int:post_id>/poll_results_json/', poll_results_json, name='poll_results_json'),

    # Grup / Kullanıcı Liderlik Tablosu
    path('leaderboard/', group_leaderboard_view, name='group_leaderboard'),
    
    path('ajax/like-post/', ajax_like_post_view, name='ajax_like_post'),

]
