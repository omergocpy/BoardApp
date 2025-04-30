# models.py dosyasını tamamen temizleyelim ve düzenleyelim
# Tüm modelleri tek bir düzenli dosyada birleştirelim

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    media = models.FileField(
        upload_to='posts/',
        null=True,
        blank=True,
        verbose_name="Medya (Resim/Video)"
    )
    
    is_bold = models.BooleanField(default=False, verbose_name="Kalın Yazı")
    text_color = models.CharField(max_length=20, null=True, blank=True, verbose_name="Yazı Rengi")
    bg_color = models.CharField(max_length=20, null=True, blank=True, verbose_name="Arka Plan Rengi")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    approved = models.BooleanField(default=False, verbose_name="Onaylandı mı?")
    points_added = models.BooleanField(default=False, verbose_name="Puan Eklendi mi?")

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
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
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
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name="Kullanıcı"
    )
    content = models.TextField(verbose_name="Yorum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yorum Tarihi")
    
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='comment_likes',
        blank=True,
        verbose_name="Beğeniler"
    )
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
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
    points_added = models.BooleanField(default=False, verbose_name="Puan Eklendi mi?")

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
    approved = models.BooleanField(default=False, verbose_name="Onaylandı mı?")
    points_added = models.BooleanField(default=False, verbose_name="Puan Eklendi mi?")

    class Meta:
        unique_together = ('post', 'user')
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
    approved = models.BooleanField(default=False, verbose_name="Onaylandı mı?")
    points_added = models.BooleanField(default=False, verbose_name="Puan Eklendi mi?")

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = "Puan"
        verbose_name_plural = "Puanlar"


# Signal fonksiyonları:

@receiver(post_save, sender=Post)
def update_post_points(sender, instance, **kwargs):
    """Post onaylandığında ve puan henüz eklenmemişse puan ekler"""
    if instance.approved and not instance.points_added:
        try:
            # Progress modelini import et
            from users.models import Progress
            
            # Kullanıcının progress nesnesini al veya oluştur
            progress, created = Progress.objects.get_or_create(user=instance.user)
            
            # Post tipine göre puan belirle
            if instance.post_type == 'text':
                points = 30
            elif instance.post_type == 'photo':
                points = 40
            elif instance.post_type == 'video':
                points = 50
            elif instance.post_type == 'poll':
                points = 45
            else:
                points = 30
            
            # Puanları ekle
            progress.points += points
            progress.save()
            
            # Kategorideki ilk paylaşım bonusu
            if instance.category and Post.objects.filter(category=instance.category, approved=True).count() == 1:
                progress.points += 50
                progress.save()
            
            # Puanlar eklendi olarak işaretle
            instance.points_added = True
            Post.objects.filter(id=instance.id).update(points_added=True)
            
            print(f"POST PUAN EKLENDİ: {instance.user.username} - (+{points})")
        except Exception as e:
            print(f"POST PUAN HATASI: {str(e)}")


@receiver(post_save, sender=Comment)
def update_comment_points(sender, instance, **kwargs):
    """Yorum onaylandığında ve puan henüz eklenmemişse puan ekler"""
    if instance.approved and not instance.points_added:
        try:
            # Progress modelini import et
            from users.models import Progress
            
            # Kullanıcının progress nesnesini al veya oluştur
            progress, created = Progress.objects.get_or_create(user=instance.user)
            
            # Yorum için 5 puan ekle
            progress.points += 5
            progress.save()
            
            # Puanlar eklendi olarak işaretle
            instance.points_added = True
            Comment.objects.filter(id=instance.id).update(points_added=True)
            
            print(f"YORUM PUAN EKLENDİ: {instance.user.username} - (+5)")
        except Exception as e:
            print(f"YORUM PUAN HATASI: {str(e)}")


@receiver(post_save, sender=Like)
def update_like_points(sender, instance, **kwargs):
    """Beğeni onaylandığında ve puan henüz eklenmemişse puan ekler"""
    print(f"LİKE SİGNAL ÇALIŞTI: Like ID={instance.id}, Approved={instance.approved}, Points_Added={instance.points_added}")
    
    if instance.approved and not instance.points_added:
        # Kendi gönderisini beğenmiyorsa puan ver
        try:
            from users.models import Progress
            
            # Progress kaydı var mı kontrol et
            try:
                progress = Progress.objects.get(user=instance.user)
                old_points = progress.points
                
                # Beğeni türüne göre güncelle
                if instance.like_type == "like":
                    progress.points += 10
                else:
                    progress.points -= 10
                
                # Progress kaydını kaydet
                progress.save()
                
                # Beğeniyi işaretle
                instance.points_added = True
                Like.objects.filter(id=instance.id).update(points_added=True)
                
                print(f"BEĞENİ PUANI GÜNCELLENDİ: {instance.user.username}: {old_points} -> {progress.points}")
                
            except Progress.DoesNotExist:
                # Kullanıcının progress kaydı yoksa oluştur
                points = 10 if instance.like_type == "like" else -10
                Progress.objects.create(user=instance.user, points=points, level=1)
                
                # Beğeniyi işaretle
                instance.points_added = True
                Like.objects.filter(id=instance.id).update(points_added=True)
                
                print(f"YENİ PROGRESS KAYDI OLUŞTURULDU: {instance.user.username} için {points} puan")
        
        except Exception as e:
            print(f"BEĞENİ HATASI: {str(e)}")
            import traceback
            print(traceback.format_exc())



@receiver(post_save, sender=Rating)
def update_rating_points(sender, instance, **kwargs):
    """Derecelendirme onaylandığında ve puan henüz eklenmemişse puan ekler"""
    if instance.approved and not instance.points_added:
        try:
            # Kendi gönderisini derecelendirmiyorsa puan ver
            if instance.user.id != instance.post.user.id:
                # Progress modelini import et
                from users.models import Progress
                
                # POST SAHİBİNİN progress nesnesini al veya oluştur
                progress, created = Progress.objects.get_or_create(user=instance.post.user)
                
                # Puan miktarını hesapla
                points_to_add = instance.score * 5
                
                # Puanları ekle
                progress.points += points_to_add
                progress.save()
                
                # Puanlar eklendi olarak işaretle
                instance.points_added = True
                Rating.objects.filter(id=instance.id).update(points_added=True)
                
                print(f"DERECELENDİRME PUAN EKLENDİ: {instance.post.user.username} - (+{points_to_add})")
        except Exception as e:
            print(f"DERECELENDİRME PUAN HATASI: {str(e)}")