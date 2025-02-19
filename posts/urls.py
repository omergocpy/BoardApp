from django.urls import path
from .views import post_list_view, post_create_view, post_detail_view, like_post_view, rate_post_view, like_comment_view, reply_comment_view, dislike_comment_view,logout_view

urlpatterns = [
    path('', post_list_view, name='post_list'),
    path('create/', post_create_view, name='post_create'),
    path('post/<int:post_id>/', post_detail_view, name='post_detail'),
    path('post/<int:post_id>/like/', like_post_view, name='like_post'),
    path('post/<int:post_id>/rate/', rate_post_view, name='rate_post'),
    path('comment/<int:comment_id>/like/', like_comment_view, name='like_comment'),
    path('comment/<int:comment_id>/dislike/', dislike_comment_view, name='dislike_comment'),
    path('comment/<int:comment_id>/reply/', reply_comment_view, name='reply_comment'),
    path('logout/', logout_view, name='logout'),  

]
