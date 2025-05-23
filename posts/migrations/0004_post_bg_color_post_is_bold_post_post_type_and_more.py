# Generated by Django 5.1 on 2025-02-20 08:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_alter_category_options_alter_category_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='bg_color',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Arka Plan Rengi'),
        ),
        migrations.AddField(
            model_name='post',
            name='is_bold',
            field=models.BooleanField(default=False, verbose_name='Kalın Yazı'),
        ),
        migrations.AddField(
            model_name='post',
            name='post_type',
            field=models.CharField(choices=[('text', 'Metin'), ('photo', 'Fotoğraf'), ('video', 'Video'), ('poll', 'Anket')], default='text', max_length=10, verbose_name='Gönderi Türü'),
        ),
        migrations.AddField(
            model_name='post',
            name='text_color',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Yazı Rengi'),
        ),
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='posts.category', verbose_name='Kategori'),
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='poll', to='posts.post', verbose_name='İlgili Gönderi')),
            ],
            options={
                'verbose_name': 'Anket',
                'verbose_name_plural': 'Anketler',
            },
        ),
        migrations.CreateModel(
            name='PollOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=100, verbose_name='Seçenek Metni')),
                ('votes', models.PositiveIntegerField(default=0, verbose_name='Oy Sayısı')),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='posts.poll', verbose_name='Anket')),
            ],
            options={
                'verbose_name': 'Anket Seçeneği',
                'verbose_name_plural': 'Anket Seçenekleri',
            },
        ),
    ]
