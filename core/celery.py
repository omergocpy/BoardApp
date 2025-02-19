# core/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django settings dosyasını belirtin
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Django settings'den ayarları al
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tüm uygulamalardaki tasks.py dosyalarını otomatik olarak keşfet
app.autodiscover_tasks()
