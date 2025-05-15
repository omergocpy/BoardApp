from django.contrib import admin
from .models import CustomUser, RegistrationCode, Group, Evaluation, SurveyCompletion, InitialSurvey, UserSurveyResponse, Team, UserSession
from django.utils.html import format_html
from django.db.models import Avg

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time', 'duration_str', 'ip_address', 'get_browser')
    list_filter = ('login_time', 'logout_time', 'user')
    search_fields = ('user__username', 'ip_address')
    date_hierarchy = 'login_time'
    
    def get_browser(self, obj):
        """Tarayıcı bilgisini kısaltılmış olarak göster"""
        if obj.user_agent:
            # Sadece ilk 30 karakterini göster
            return obj.user_agent[:30] + "..." if len(obj.user_agent) > 30 else obj.user_agent
        return "-"
    get_browser.short_description = "Tarayıcı"

@admin.register(SurveyCompletion)
class SurveyCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'completed', 'completed_at', 'second_survey_completed', 'second_survey_completed_at', 'second_survey_reminder_sent')
    list_filter = ('completed', 'second_survey_completed', 'second_survey_reminder_sent')
    search_fields = ('user__username',)
    
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'get_member_count', 'get_total_points', 'created_at')
    list_filter = ('group',)
    search_fields = ('name', 'description')
    
    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = 'Üye Sayısı'
    
    def get_total_points(self, obj):
        return obj.get_total_points()
    get_total_points.short_description = 'Toplam Puan'
    
    
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'gender', 'registration_code', 'get_total_sessions', 'get_total_time')
    list_filter = ('gender', 'registration_code', 'is_active')
    search_fields = ('username', 'email', 'registration_code')
    
    def get_total_sessions(self, obj):
        """Kullanıcının toplam oturum sayısı"""
        return obj.sessions.count()
    get_total_sessions.short_description = "Toplam Oturum"
    
    def get_total_time(self, obj):
        """Kullanıcının toplam sistemde kalma süresi"""
        from django.db.models import Sum, F, ExpressionWrapper, fields
        from django.db.models.functions import Coalesce
        
        # Tamamlanan oturumların sürelerini topla
        completed_sessions = obj.sessions.filter(logout_time__isnull=False)
        
        if not completed_sessions.exists():
            return "0s 0d 0sn"
        
        # Django ORM ile doğrudan hesaplama
        duration = completed_sessions.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('logout_time') - F('login_time'),
                    output_field=fields.DurationField()
                )
            )
        )['total']
        
        if duration:
            seconds = duration.total_seconds()
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours}s {minutes}d {secs}sn"
        return "0s 0d 0sn"
    get_total_time.short_description = "Toplam Süre"
    

@admin.register(RegistrationCode)
class RegistrationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'password', 'used')
    list_filter = ('used',)
    search_fields = ('code',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_team_based', 'evaluation_type', 'competition_type', 'participant_count')
    list_filter = ('evaluation_type', 'competition_type') 
    search_fields = ('name', 'evaluation_type', 'competition_type')


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('evaluator', 'evaluated_user', 'score')
    list_filter = ('score',)
    search_fields = ('evaluator__username', 'evaluated_user__username')


@admin.register(InitialSurvey)
class InitialSurveyAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active', 'created_at', 'response_count', 'average_score')
    list_filter = ('is_active',)
    search_fields = ('question',)
    ordering = ('order',)
    
    def response_count(self, obj):
        count = obj.responses.count()
        return count
    response_count.short_description = 'Cevap Sayısı'
    
    def average_score(self, obj):
        avg = obj.responses.aggregate(Avg('answer'))['answer__avg']
        if avg:
            avg = round(avg, 2)
            # Renklendirme: Düşük puanlar kırmızı, yüksek puanlar yeşil
            if avg < 3:
                color = 'red'
            elif avg < 4:
                color = 'orange'
            else:
                color = 'green'
            return format_html('<span style="color: {};">{}</span>', color, avg)
        return "-"
    average_score.short_description = 'Ortalama Puan'

# UserSurveyResponseInline sınıfını düzeltiyoruz
# Artık SurveyCompletion modeliyle değil, CustomUser ile ilişkilendiriyoruz
class UserResponseInline(admin.TabularInline):
    model = UserSurveyResponse
    extra = 0
    can_delete = False
    readonly_fields = ('question', 'answer', 'created_at')
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(UserSurveyResponse)
class UserSurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer_display', 'created_at')
    list_filter = ('answer', 'created_at', 'question')
    search_fields = ('user__username', 'question__question')
    
    def answer_display(self, obj):
        # Renklendirme: Düşük puanlar kırmızı, yüksek puanlar yeşil
        if obj.answer < 3:
            color = 'red'
        elif obj.answer < 4:
            color = 'orange'
        else:
            color = 'green'
        return format_html('<span style="color: {};">{}</span>', color, obj.get_answer_display())
    answer_display.short_description = 'Cevap'

