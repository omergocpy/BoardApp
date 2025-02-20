# myapp/models.py
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


POST_TYPES = [
    ('text', 'Metin'),
    ('photo', 'Fotoğraf'),
    ('video', 'Video'),
    ('poll', 'Anket'),
    # İsterseniz gif vs. ekleyebilirsiniz
]

class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Kullanıcı"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Kategori"
    )
    content = models.TextField(verbose_name="İçerik")
    
    post_type = models.CharField(
        max_length=10,
        choices=POST_TYPES,
        default='text',
        verbose_name="Gönderi Türü"
    )

    # Metin, foto, video vs. için tek bir 'media' alanı.
    media = models.FileField(
        upload_to='posts/',
        null=True,
        blank=True,
        verbose_name="Medya (Resim/Video)"
    )
    
    # Stil alanları (örnek)
    is_bold = models.BooleanField(default=False, verbose_name="Kalın Yazı")
    text_color = models.CharField(max_length=20, null=True, blank=True, verbose_name="Yazı Rengi")
    bg_color = models.CharField(max_length=20, null=True, blank=True, verbose_name="Arka Plan Rengi")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    approved = models.BooleanField(default=False, verbose_name="Onaylandı mı?")

    def __str__(self):
        return f"{self.user.username} - {self.content[:20]}"

    class Meta:
        verbose_name = "Gönderi"
        verbose_name_plural = "Gönderiler"


class Poll(models.Model):
    """Anket verisini tutar, Post ile 1-1 ilişki."""
    post = models.OneToOneField(
        Post,
        on_delete=models.CASCADE,
        related_name='poll',
        verbose_name="İlgili Gönderi"
    )

    def __str__(self):
        return f"Anket - {self.post.user.username}"

    class Meta:
        verbose_name = "Anket"
        verbose_name_plural = "Anketler"


class PollOption(models.Model):
    """Anketteki seçenekler ve oy sayıları."""
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="Anket"
    )
    text = models.CharField(max_length=100, verbose_name="Seçenek Metni")
    votes = models.PositiveIntegerField(default=0, verbose_name="Oy Sayısı")

    def __str__(self):
        return f"{self.text} ({self.votes} oy)"

    class Meta:
        verbose_name = "Anket Seçeneği"
        verbose_name_plural = "Anket Seçenekleri"

class PollVote(models.Model):
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    option = models.ForeignKey('PollOption', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Aynı kullanıcı aynı ankete tekrar oy veremesin:
        unique_together = ('poll', 'user')

    def __str__(self):
        return f"{self.user} -> {self.poll} ({self.option})"
    
    
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name="Gönderi"
    )
    user = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name="Kullanıcı"
    )
    content = models.TextField(verbose_name="Yorum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yorum Tarihi")
    
    likes = models.ManyToManyField(
        User,
        related_name='comment_likes',
        blank=True,
        verbose_name="Beğeniler"
    )
    dislikes = models.ManyToManyField(
        User,
        related_name='comment_dislikes',
        blank=True,
        verbose_name="Beğenmeme"
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE,
        verbose_name="Yanıt"
    )
    approved = models.BooleanField(default=False, verbose_name="Onaylandı mı?")

    def __str__(self):
        return f'{self.user.username} - {self.content[:20]}'
    
    class Meta:
        verbose_name = "Yorum"
        verbose_name_plural = "Yorumlar"


LIKE_TYPES = (
    ('like', 'Beğeni'),
    ('dislike', 'Beğenmeme'),
)

class Like(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='likes',
        on_delete=models.CASCADE,
        verbose_name="Gönderi"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='user_likes',
        on_delete=models.CASCADE,
        verbose_name="Kullanıcı"
    )
    like_type = models.CharField(
        max_length=10,
        choices=LIKE_TYPES,
        default='like',
        verbose_name="Beğeni Türü"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Beğeni Tarihi")

    class Meta:
        unique_together = ('post', 'user', 'like_type')
        verbose_name = "Beğeni"
        verbose_name_plural = "Beğeniler"


class Rating(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='ratings',
        on_delete=models.CASCADE,
        verbose_name="Gönderi"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='user_ratings',
        on_delete=models.CASCADE,
        verbose_name="Kullanıcı"
    )
    score = models.PositiveIntegerField(default=1, verbose_name="Puan")  # 1-5 arası
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Puan Tarihi")

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = "Puan"
        verbose_name_plural = "Puanlar"
