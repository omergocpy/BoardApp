# myapp/admin.py
from django.contrib import admin
from .models import Post, Comment, Like, Rating, Category, Poll, PollOption,PollVote

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 1

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    inlines = [PollOptionInline]

@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):
    list_display = ('poll', 'user', 'option', 'created_at')
    list_filter = ('poll', 'user', 'option')
    
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post_type', 'content', 'created_at', 'approved')
    list_filter = ('approved', 'post_type', 'created_at', 'user')
    search_fields = ('user__username', 'content')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'content', 'created_at', 'approved')
    list_filter = ('approved', 'created_at', 'user', 'post')
    search_fields = ('user__username', 'content', 'post__content')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'like_type', 'created_at')
    list_filter = ('like_type', 'created_at', 'user', 'post')
    search_fields = ('user__username', 'post__content')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'score', 'created_at')
    list_filter = ('score', 'created_at', 'user', 'post')
    search_fields = ('user__username', 'post__content')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
