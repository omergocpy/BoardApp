from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.utils import create_notification


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
    points_added = models.BooleanField(default=False)  # Bu alanı ekleyin

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
    """Yorum onaylandığında puan ekler"""
    if instance.approved and not instance.points_added:
        try:
            from users.models import Progress
            
            # Yorum yapan kullanıcıya puan ekle
            user_progress, created = Progress.objects.get_or_create(user=instance.user)
            user_progress.points += 10  # Yorum yapan 10 puan alır
            user_progress.check_for_level_up()
            
            # Gönderi sahibi farklı biriyse puan ekle
            if instance.user.id != instance.post.user.id:
                post_user_progress, created = Progress.objects.get_or_create(user=instance.post.user)
                post_user_progress.points += 5  # Yorum alan kullanıcı 5 puan alır
                post_user_progress.check_for_level_up()
            
            # Puanlar eklendi olarak işaretle
            instance.points_added = True
            Comment.objects.filter(id=instance.id).update(points_added=True)
            
            print(f"YORUM PUANI EKLENDİ: {instance.user.username} - (+10)")
            if instance.user.id != instance.post.user.id:
                print(f"GÖNDERİ SAHİBİ YORUM PUANI EKLENDİ: {instance.post.user.username} - (+5)")
            
        except Exception as e:
            print(f"YORUM PUAN HATASI: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
@receiver(post_save, sender=Like)
def update_like_points(sender, instance, **kwargs):
    """Beğeni onaylandığında puan ekler"""
    if instance.approved and not instance.points_added:
        try:
            from users.models import Progress
            
            # Beğenen kullanıcı için puan ekle
            user_progress, created = Progress.objects.get_or_create(user=instance.user)
            
            # Her zaman beğeni için puan ekle (like veya dislike)
            user_progress.points += 5
            user_progress.check_for_level_up()
            
            # Gönderi sahibi farklı biriyse ve bu bir like ise, gönderi sahibine de puan ekle
            if instance.user.id != instance.post.user.id and instance.like_type == 'like':
                post_user_progress, created = Progress.objects.get_or_create(user=instance.post.user)
                post_user_progress.points += 5  # Beğeni alan kullanıcı 5 puan kazanır
                post_user_progress.check_for_level_up()
            
            # Puanlar eklendi olarak işaretle
            instance.points_added = True
            Like.objects.filter(id=instance.id).update(points_added=True)
            
            print(f"BEĞENİ PUANI EKLENDİ: {instance.user.username} - (+5)")
            if instance.user.id != instance.post.user.id and instance.like_type == 'like':
                print(f"GÖNDERİ SAHİBİ PUAN EKLENDİ: {instance.post.user.username} - (+5)")
                
        except Exception as e:
            print(f"BEĞENİ PUAN HATASI: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
            
@receiver(post_save, sender=Rating)
def update_rating_points(sender, instance, **kwargs):
    """Derecelendirme onaylandığında puan ekler"""
    if instance.approved and not instance.points_added:
        try:
            from users.models import Progress
            
            # Derecelendirme yapan kullanıcıya puan ekle
            user_progress, created = Progress.objects.get_or_create(user=instance.user)
            user_progress.points += 5  # Derecelendirme yapan her zaman 5 puan alır
            user_progress.check_for_level_up()
            
            # Gönderi sahibi farklı biriyse, ona yıldız sayısı * 5 puan ekle
            if instance.user.id != instance.post.user.id:
                post_user_progress, created = Progress.objects.get_or_create(user=instance.post.user)
                points_to_add = instance.score * 5  # 5 yıldız = 25 puan, 4 yıldız = 20 puan, vs.
                post_user_progress.points += points_to_add
                post_user_progress.check_for_level_up()
                
                print(f"DERECELENDİRME PUANI EKLENDİ: Derecelendiren: {instance.user.username} (+5), " 
                      f"Gönderi Sahibi: {instance.post.user.username} (+{points_to_add})")
            
            # Puanlar eklendi olarak işaretle
            instance.points_added = True
            Rating.objects.filter(id=instance.id).update(points_added=True)
            
        except Exception as e:
            print(f"DERECELENDİRME PUAN HATASI: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
            
@receiver(post_save, sender=PollVote)            
def update_poll_vote_points(sender, instance, **kwargs):
    """Anket katılımında puan ekler"""
    if not getattr(instance, 'points_added', False):
        try:
            from users.models import Progress
            
            # Ankete katılan kullanıcıya puan ekle
            user_progress, created = Progress.objects.get_or_create(user=instance.user)
            user_progress.points += 5  # Ankete katılan 5 puan alır
            user_progress.check_for_level_up()
            
            # Anket sahibi farklı biriyse puan ekle
            if instance.user.id != instance.poll.post.user.id:
                poll_owner_progress, created = Progress.objects.get_or_create(user=instance.poll.post.user)
                poll_owner_progress.points += 3  # Anket sahibi her katılım için 3 puan alır
                poll_owner_progress.check_for_level_up()
            
            # Puanlar eklendi olarak işaretle
            setattr(instance, 'points_added', True)
            
            print(f"ANKET KATILIM PUANI EKLENDİ: {instance.user.username} - (+5)")
            if instance.user.id != instance.poll.post.user.id:
                print(f"ANKET SAHİBİ PUAN EKLENDİ: {instance.poll.post.user.username} - (+3)")
            
        except Exception as e:
            print(f"ANKET KATILIM PUAN HATASI: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    """Beğeni eklendiğinde bildirim gönder"""
    if created and instance.user != instance.post.user:
        notification_text = f"{instance.user.username} gönderinizi beğendi."
        create_notification(
            recipient=instance.post.user,
            sender=instance.user,
            notification_type='like',
            text=notification_text,
            post=instance.post
        )

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    """Yorum eklendiğinde bildirim gönder"""
    if created and instance.user != instance.post.user:
        notification_text = f"{instance.user.username} gönderinize yorum yaptı."
        create_notification(
            recipient=instance.post.user,
            sender=instance.user,
            notification_type='comment',
            text=notification_text,
            post=instance.post,
            comment=instance
        )