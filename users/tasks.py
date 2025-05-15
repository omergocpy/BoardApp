from celery import shared_task
import datetime
from .models import SurveyCompletion
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import UserSession

@shared_task
def check_and_close_stale_sessions():
    """
    30 dakikadan uzun süredir aktif olmayan ve logout olmayan oturumları kapatır
    """
    # 30+ dakika önce oluşturulan ve hala açık olan oturumları bul
    stale_time = timezone.now() - timedelta(minutes=30)
    stale_sessions = UserSession.objects.filter(
        login_time__lt=stale_time,
        logout_time__isnull=True
    )
    
    # Bu oturumları kapat
    count = 0
    for session in stale_sessions:
        session.logout_time = session.login_time + timedelta(minutes=30)  # Varsayılan 30 dakika oturum süresi
        session.save()
        count += 1
    
    return f"{count} eski oturum kapatıldı"

@shared_task
def check_second_survey_due():
    """
    14 gün sonra ikinci anket için kullanıcıları kontrol eder.
    """
    # İlk anketi tamamlamış ama ikinci anketi tamamlamamış kullanıcıları bul
    survey_completions = SurveyCompletion.objects.filter(
        completed=True,
        second_survey_completed=False,
        second_survey_reminder_sent=False
    )
    
    for completion in survey_completions:
        if completion.completed_at:
            fourteen_days_later = completion.completed_at + datetime.timedelta(days=14)
            
            if timezone.now() >= fourteen_days_later:
                completion.second_survey_reminder_sent = True
                completion.save()
                
                print(f"User {completion.user.username} is due for second survey!")
    
    return len(survey_completions)