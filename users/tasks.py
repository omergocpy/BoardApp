from celery import shared_task
from django.utils import timezone
import datetime
from .models import SurveyCompletion

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