from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Sum

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
    component = models.CharField('Bileşen', max_length=50, null=True, blank=True)  
    participant_count = models.PositiveIntegerField('Katılımcı Sayısı', default=0)
    level = models.IntegerField('Grup Seviyesi', default=1)  

    class Meta:
        verbose_name = 'Grup'
        verbose_name_plural = 'Gruplar'

    def __str__(self):
        return self.get_name_display()

    def is_team_based_group(self):
        """Grup takım bazlı mı?"""
        return self.name in ['C', 'D', 'F'] 
    
    def get_teams_leaderboard(self):
        """Gruptaki takımların sıralamasını döndürür (takım bazlı gruplar için)"""
        if not self.is_team_based():
            return []
        
        teams = self.teams.all()
        team_points = []
        
        for team in teams:
            total_points = team.get_total_points()
            team_points.append({
                'team': team,
                'points': total_points
            })
        
        sorted_teams = sorted(team_points, key=lambda x: x['points'], reverse=True)
        
        for i, team_data in enumerate(sorted_teams):
            team_data['rank'] = i + 1
        
        return sorted_teams

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
    FEATURE_LEVELS = {
        'can_use_bold_text': 2,
        'can_use_colored_text': 3,
        'can_use_background': 4,
        'can_share_gif': 5,
        'can_share_photo': 6,
        'can_share_audio': 7,
        'can_share_video': 8,
        'can_spin_wheel': 9,
        'can_choose_reward': 10,
    }
    
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
    def get_feature_details(self):
        """Tüm özelliklerin durumunu ve açılması için gereken seviyeleri döndürür"""
        features = []
        
        for feature_name, required_level in self.FEATURE_LEVELS.items():
            # Metod adını özellik isme dönüştür (can_use_bold_text -> Kalın Yazı gibi)
            display_name = feature_name.replace('can_', '').replace('_', ' ').title()
            
            # Gerekli puanı hesapla
            required_points = self.LEVEL_THRESHOLDS.get(required_level, 0)
            
            # Özelliğin açık olup olmadığını kontrol et
            is_unlocked = getattr(self, feature_name)()
            
            features.append({
                'name': display_name,
                'feature_name': feature_name,
                'required_level': required_level,
                'required_points': required_points,
                'is_unlocked': is_unlocked,
            })
        
        return features
    
    def get_progress_percentage(self):
        current_level_threshold = self.LEVEL_THRESHOLDS.get(self.level, 0)
        next_level_threshold = self.LEVEL_THRESHOLDS.get(self.level + 1, current_level_threshold)

        if next_level_threshold == current_level_threshold:
            return 100  # Eğer kullanıcı maksimum seviyedeyse, yüzde 100 döndür

        # Mevcut seviyedeki ilerleme (bu seviyede kaç puan kazanıldı)
        progress_in_level = self.points - current_level_threshold
        # Bir sonraki seviyeye geçmek için gereken puan miktarı
        points_needed_for_next_level = next_level_threshold - current_level_threshold

        # Yüzde olarak ilerleme (0-100 arası)
        percentage = (progress_in_level / points_needed_for_next_level) * 100
        return max(0, min(100, percentage))

    def get_level_progress_text(self):
        current_level_threshold = self.LEVEL_THRESHOLDS.get(self.level, 0)
        next_level_threshold = self.LEVEL_THRESHOLDS.get(self.level + 1, current_level_threshold)
        
        if next_level_threshold == current_level_threshold:
            return f"Seviye {self.level} (Maksimum)"
        
        # Mevcut seviyedeki ilerleme
        progress_in_level = self.points - current_level_threshold
        # Bir sonraki seviyeye geçmek için gereken toplam puan
        points_needed_for_next_level = next_level_threshold - current_level_threshold
        
        return f"Seviye {self.level} ({progress_in_level}/{points_needed_for_next_level})"
    
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
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
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

LIKERT_CHOICES = [
    (1, 'Kesinlikle katılmıyorum'),
    (2, 'Katılmıyorum'),
    (3, 'Kısmen katılmıyorum'),
    (4, 'Kısmen katılıyorum'),
    (5, 'Katılıyorum'),
    (6, 'Kesinlikle katılıyorum'),
]

class InitialSurvey(models.Model):
    """Başlangıç anketi modeli - anket sorularını tutar"""
    question = models.CharField(max_length=255, verbose_name="Soru")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    
    class Meta:
        verbose_name = "Anket Sorusu"
        verbose_name_plural = "Anket Soruları"
        ordering = ['order']  # Soruları sıralamaya göre göster
    
    def __str__(self):
        return self.question

class UserSurveyResponse(models.Model):
    """Kullanıcı anket cevaplarını tutar"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                             related_name='survey_responses', verbose_name="Kullanıcı")
    question = models.ForeignKey(InitialSurvey, on_delete=models.CASCADE, 
                                related_name='responses', verbose_name="Soru")
    answer = models.IntegerField(choices=LIKERT_CHOICES, verbose_name="Cevap")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Cevap Tarihi")
    
    is_second_response = models.BooleanField(default=False, verbose_name="İkinci Cevap mı?")
    
    class Meta:
        verbose_name = "Kullanıcı Cevabı"
        verbose_name_plural = "Kullanıcı Cevapları"
        unique_together = ('user', 'question', 'is_second_response')
    
    def __str__(self):
        survey_type = "İkinci Anket" if self.is_second_response else "İlk Anket"
        return f"{self.user.username} - {survey_type} - {self.question} - {self.get_answer_display()}"

class SurveyCompletion(models.Model):
    """Kullanıcının anketi tamamlayıp tamamlamadığını tutar"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='survey_completion', verbose_name="Kullanıcı")
    completed = models.BooleanField(default=False, verbose_name="Tamamlandı mı?")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Tamamlanma Tarihi")
    
    # Yeni eklenecek alanlar
    second_survey_completed = models.BooleanField(default=False, verbose_name="İkinci Anket Tamamlandı mı?")
    second_survey_completed_at = models.DateTimeField(null=True, blank=True, verbose_name="İkinci Anket Tamamlanma Tarihi")
    second_survey_reminder_sent = models.BooleanField(default=False, verbose_name="İkinci Anket Hatırlatması Gönderildi mi?")
    
    class Meta:
        verbose_name = "Anket Tamamlama"
        verbose_name_plural = "Anket Tamamlamalar"
    
    def __str__(self):
        if self.second_survey_completed:
            status = "Her iki anket tamamlandı"
        elif self.completed:
            status = "İlk anket tamamlandı"
        else:
            status = "Tamamlanmadı"
        return f"{self.user.username} - {status}"
    
    def is_second_survey_due(self):
        """İkinci anketin gösterilme zamanı geldi mi?"""
        if not self.completed or self.second_survey_completed:
            return False
        
        if self.completed_at:
            # 14 gün sonrası için kontrol
            from django.utils import timezone
            import datetime
            
            fourteen_days_later = self.completed_at + datetime.timedelta(days=14)
            return timezone.now() >= fourteen_days_later
        
        return False
    
class Team(models.Model):
    name = models.CharField('Takım Adı', max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='teams', verbose_name='Grup')
    description = models.TextField('Takım Açıklaması', null=True, blank=True)
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Takım'
        verbose_name_plural = 'Takımlar'
        unique_together = ('name', 'group')  
    
    def __str__(self):
        return f"{self.name} ({self.group.get_name_display()})"
    
    def get_total_points(self):
        """Takımdaki tüm üyelerin toplam puanını hesaplar"""
        return Progress.objects.filter(user__team=self).aggregate(Sum('points'))['points__sum'] or 0
        
    def get_member_count(self):
        """Takımdaki üye sayısını döndürür"""
        return self.members.count()