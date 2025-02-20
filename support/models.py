# myapp/models.py
from django.db import models
from django.conf import settings

class SupportRequest(models.Model):
    STATUS_CHOICES = [
        ('open', 'Açık'),
        ('closed', 'Kapalı'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Kullanıcı"
    )
    subject = models.CharField(max_length=100, verbose_name="Konu")
    message = models.TextField(verbose_name="Mesaj")
    attachment = models.ImageField(
        upload_to='support_attachments/',
        null=True,
        blank=True,
        verbose_name="Dosya Eki"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name="Durum"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Destek Talebi"
        verbose_name_plural = "Destek Talepleri"

    def __str__(self):
        return f"{self.subject} - {self.user.username}"

class Message(models.Model):
    support_request = models.ForeignKey(
        SupportRequest,
        related_name='messages',
        on_delete=models.CASCADE,
        verbose_name="Destek Talebi"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Gönderen"
    )
    content = models.TextField(verbose_name="Mesaj İçeriği")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Gönderilme Tarihi")

    class Meta:
        verbose_name = "Mesaj"
        verbose_name_plural = "Mesajlar"

    def __str__(self):
        return f"Message by {self.sender.username} on {self.created_at}"
