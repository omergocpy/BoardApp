from django.contrib import admin
from .models import CustomUser, RegistrationCode, Group, Evaluation

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
    list_filter = ('is_team_based', 'evaluation_type', 'competition_type')
    search_fields = ('name', 'evaluation_type', 'competition_type')


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('evaluator', 'evaluated_user', 'score')
    list_filter = ('score',)
    search_fields = ('evaluator__username', 'evaluated_user__username')
