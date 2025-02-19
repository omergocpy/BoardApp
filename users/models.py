from django.db import models
from django.contrib.auth.models import AbstractUser

class Group(models.Model):
    GROUP_TYPES = [
        ('A', 'Grup A'),
        ('B', 'Grup B'),
        ('C', 'Grup C'),
        ('D', 'Grup D'),
        ('E', 'Grup E'),
        ('F', 'Grup F'),
    ]
    
    name = models.CharField('Grup Adı', max_length=1, choices=GROUP_TYPES, unique=True)
    is_team_based = models.BooleanField('Takım Bazlı mı?', default=False)
    evaluation_type = models.CharField('Değerlendirme Türü', max_length=50)
    competition_type = models.CharField('Yarışma Türü', max_length=50)
    component = models.CharField('Bileşen', max_length=50, null=True, blank=True)  # Leaderboard, Progress bar, etc.
    participant_count = models.PositiveIntegerField('Katılımcı Sayısı', default=0)
    level = models.IntegerField('Grup Seviyesi', default=1)  # Grup seviyesi için alan eklendi

    class Meta:
        verbose_name = 'Grup'
        verbose_name_plural = 'Gruplar'

    def __str__(self):
        return self.get_name_display()


class RegistrationCode(models.Model):
    code = models.CharField('Kod', max_length=6, unique=True)
    password = models.CharField('Şifre', max_length=6)
    used = models.BooleanField('Kullanıldı mı?', default=False)

    class Meta:
        verbose_name = 'Kayıt Kodu'
        verbose_name_plural = 'Kayıt Kodları'

    def __str__(self):
        return self.code

class Progress(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='progress_instance')
    level = models.IntegerField('Seviye', default=1)
    points = models.IntegerField('Puan', default=0)

    LEVEL_THRESHOLDS = {
        1: 0,
        2: 100,
        3: 250,
        4: 400,
        5: 500,
        6: 650,
        7: 800,
        8: 1000,
        9: 1500,
        10: 2000,
    }

    def get_progress_percentage(self):
        current_level_threshold = self.LEVEL_THRESHOLDS.get(self.level, 0)
        next_level_threshold = self.LEVEL_THRESHOLDS.get(self.level + 1, current_level_threshold)

        if next_level_threshold == current_level_threshold:
            return 100  # Eğer kullanıcı maksimum seviyedeyse, yüzde 100 döndür

        progress_in_level = self.points - current_level_threshold
        level_range = next_level_threshold - current_level_threshold

        return max(0, min(100, (progress_in_level / level_range) * 100))
    
    def check_for_level_up(self):
        if self.points >= 2000:
            self.level = 10
        elif self.points >= 1500:
            self.level = 9
        elif self.points >= 1000:
            self.level = 8
        elif self.points >= 800:
            self.level = 7
        elif self.points >= 650:
            self.level = 6
        elif self.points >= 500:
            self.level = 5
        elif self.points >= 400:
            self.level = 4
        elif self.points >= 250:
            self.level = 3
        elif self.points >= 100:
            self.level = 2
        self.save()

    def can_use_bold_text(self):
        return self.level >= 2
    
    def can_use_colored_text(self):
        return self.level >= 3
    
    def can_use_background(self):
        return self.level >= 4

    def can_share_gif(self):
        return self.level >= 5

    def can_share_photo(self):
        return self.level >= 6
    
    def can_share_audio(self):
        return self.level >= 7
    
    def can_share_video(self):
        return self.level >= 8

    def can_spin_wheel(self):
        return self.level >= 9
    
    def can_choose_reward(self):
        return self.level >= 10
    

class CustomUser(AbstractUser):
    registration_code = models.CharField('Kayıt Kodu', max_length=6, unique=True, null=True, blank=True)
    gender = models.CharField('Cinsiyet', max_length=10, choices=[('male', 'Erkek'), ('female', 'Kadın'), ('other', 'Diğer')])
    avatar = models.CharField('Avatar', max_length=100, null=True, blank=True)
    registration_code_used = models.CharField('Kullanılan Kayıt Kodu', max_length=6, null=True, blank=True)
    progress = models.OneToOneField(Progress, on_delete=models.CASCADE, null=True, blank=True, related_name='user_progress')
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'

    def __str__(self):
        return self.username


class Evaluation(models.Model):
    evaluator = models.ForeignKey(CustomUser, related_name='evaluator', on_delete=models.CASCADE, verbose_name='Değerlendiren')
    evaluated_user = models.ForeignKey(CustomUser, related_name='evaluated_user', on_delete=models.CASCADE, verbose_name='Değerlendirilen Kullanıcı')
    score = models.PositiveIntegerField('Puan', default=0)
    feedback = models.TextField('Geri Bildirim', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Değerlendirme'
        verbose_name_plural = 'Değerlendirmeler'

    def __str__(self):
        return f"{self.evaluator.username} tarafından {self.evaluated_user.username} için değerlendirme"




        