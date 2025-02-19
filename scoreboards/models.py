from django.db import models
from users.models import CustomUser

class Competition(models.Model):
    name = models.CharField(max_length=100, verbose_name="Yarışma Adı")
    description = models.TextField(null=True, blank=True, verbose_name="Yarışma Açıklaması")
    start_date = models.DateTimeField(verbose_name="Başlangıç Tarihi")
    end_date = models.DateTimeField(verbose_name="Bitiş Tarihi")

    class Meta:
        verbose_name = "Yarışma"
        verbose_name_plural = "Yarışma"

    def __str__(self):
        return self.name


class Scoreboard(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, verbose_name="Yarışma")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    rank = models.PositiveIntegerField(verbose_name="Sıralama")
    score = models.PositiveIntegerField(verbose_name="Skor")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Skor Tablosu"
        verbose_name_plural = "Skor Tablosu"
        ordering = ['-score']  

    def __str__(self):
        return f"{self.user.username} - {self.competition}: {self.score} Puan"