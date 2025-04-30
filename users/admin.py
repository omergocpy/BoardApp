from django.contrib import admin
from .models import CustomUser, RegistrationCode, Group, Evaluation, SurveyCompletion, InitialSurvey, UserSurveyResponse, Team
from django.utils.html import format_html
from django.db.models import Avg


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
    list_display = ('username', 'email', 'gender', 'registration_code')
    list_filter = ('gender', 'registration_code')
    search_fields = ('username', 'email', 'registration_code')


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

