from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Kategori Adı")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Kategori")
    content = models.TextField(verbose_name="İçerik")
    media = models.FileField(upload_to='posts/', null=True, blank=True, verbose_name="Medya (Resim/Video)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    approved = models.BooleanField(default=False, verbose_name="Onaylandı mı?")

    def __str__(self):
        return self.content[:20]

    class Meta:
        verbose_name = "Gönderi"
        verbose_name_plural = "Gönderiler"

class Comment(models.Model):
    post = models.ForeignKey('Post', related_name='comments', on_delete=models.CASCADE, verbose_name="Gönderi")
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE, verbose_name="Kullanıcı")
    content = models.TextField(verbose_name="Yorum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yorum Tarihi")
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True, verbose_name="Beğeniler")
    dislikes = models.ManyToManyField(User, related_name='comment_dislikes', blank=True, verbose_name="Beğenmeme")
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE, verbose_name="Yanıt")
    approved = models.BooleanField(default=False, verbose_name="Onaylandı mı?")

    def __str__(self):
        return f'{self.user.username} - {self.post}'
    
    class Meta:
        verbose_name = "Yorum"
        verbose_name_plural = "Yorumlar"

class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE, verbose_name="Gönderi")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_likes', on_delete=models.CASCADE, verbose_name="Kullanıcı")
    like_type = models.CharField(max_length=10, choices=(('like', 'Beğeni'), ('dislike', 'Beğenmeme')), default='like', verbose_name="Beğeni Türü")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Beğeni Tarihi")

    class Meta:
        unique_together = ('post', 'user', 'like_type')
        verbose_name = "Beğeni"
        verbose_name_plural = "Beğeniler"

class Rating(models.Model):
    post = models.ForeignKey(Post, related_name='ratings', on_delete=models.CASCADE, verbose_name="Gönderi")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_ratings', on_delete=models.CASCADE, verbose_name="Kullanıcı")
    score = models.PositiveIntegerField(default=1, verbose_name="Puan")  # 1-5 arası puan
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Puan Tarihi")

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = "Puan"
        verbose_name_plural = "Puanlar"
