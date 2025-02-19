from django.db import models
from django.conf import settings

class SupportRequest(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Teknik Destek'),
        ('billing', 'Fatura Desteği'),
        ('general', 'Genel Soru'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Kategori")
    subject = models.CharField(max_length=100, verbose_name="Konu")
    message = models.TextField(verbose_name="Mesaj")
    status = models.CharField(max_length=20, choices=[('open', 'Açık'), ('closed', 'Kapalı')], default='open', verbose_name="Durum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Destek Talebi"
        verbose_name_plural = "Destek Talepleri"

    def __str__(self):
        return f"{self.subject} ({self.get_category_display()}) - {self.user.username}"


class Message(models.Model):
    support_request = models.ForeignKey(SupportRequest, related_name='messages', on_delete=models.CASCADE, verbose_name="Destek Talebi")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Gönderen")
    content = models.TextField(verbose_name="İleti")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Gönderilme Tarihi")

    class Meta:
        verbose_name = "Mesaj"
        verbose_name_plural = "Mesajlar"

    def __str__(self):
        return f"Message by {self.sender.username} on {self.created_at}"
