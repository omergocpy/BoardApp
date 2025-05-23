from django.contrib import admin
from .models import SupportRequest, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 1

@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    # Kategori olmadığı için 'category' çıkarıldı, istersek 'attachment' ekleyebiliriz.
    list_display = ('subject', 'attachment', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'user__username')
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('support_request', 'sender', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'sender__username')
