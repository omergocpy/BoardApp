from .models import Notification

def create_notification(recipient, sender, notification_type, text, post=None, comment=None):
    """
    Bildirim oluşturma yardımcı fonksiyonu
    """
    # Kendi kendine bildirim göndermeyi önle
    if recipient == sender:
        return None
    
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        text=text,
        post=post,
        comment=comment
    )
    
    return notification