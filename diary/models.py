from django.db import models
from django.contrib.auth.models import User


class Mood(models.Model):
    name = models.CharField(max_length=50, blank=True)  # 任意（将来用）
    color = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name or self.color or "—"


class Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    mood = models.ForeignKey(Mood, on_delete=models.SET_NULL, null=True, blank=True, related_name="records")
    note = models.TextField(blank=True)
    photo = models.ImageField(upload_to="photos/", blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "date"], name="uniq_record_user_date"),
        ]
        ordering = ["-date"]  # 任意：新しい日付が上に来るように
