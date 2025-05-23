# Generated by Django 5.1 on 2024-10-21 07:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='İleti')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Gönderilme Tarihi')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Gönderen')),
                ('support_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='support.supportrequest', verbose_name='Destek Talebi')),
            ],
            options={
                'verbose_name': 'Mesaj',
                'verbose_name_plural': 'Mesajlar',
            },
        ),
    ]
