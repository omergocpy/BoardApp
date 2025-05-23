# Generated by Django 5.1 on 2024-09-09 19:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('technical', 'Teknik Destek'), ('billing', 'Fatura Desteği'), ('general', 'Genel Soru')], max_length=50, verbose_name='Kategori')),
                ('subject', models.CharField(max_length=100, verbose_name='Konu')),
                ('message', models.TextField(verbose_name='Mesaj')),
                ('status', models.CharField(choices=[('open', 'Açık'), ('closed', 'Kapalı')], default='open', max_length=20, verbose_name='Durum')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Kullanıcı')),
            ],
            options={
                'verbose_name': 'Destek Talebi',
                'verbose_name_plural': 'Destek Talepleri',
            },
        ),
    ]
