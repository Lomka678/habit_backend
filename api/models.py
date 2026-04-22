from django.db import models
from django.contrib.auth.models import User

class Habit(models.Model):
    FREQ_CHOICES = [
        ('DAILY', 'Каждый день'),
        ('WEEKLY', 'По дням недели'),
        ('INTERVAL', 'Интервал'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    target_daily_count = models.IntegerField(default=1)
    end_date = models.DateField(null=True, blank=True)

    # --- НОВЫЕ ПОЛЯ РАСПИСАНИЯ ---
    frequency_type = models.CharField(max_length=10, choices=FREQ_CHOICES, default='DAILY')
    days_of_week = models.CharField(max_length=20, blank=True, null=True) # Например: "1,3,5" (Пн, Ср, Пт)
    interval = models.IntegerField(default=1) # Например: 2 (раз в 2 дня)

    def __str__(self):
        return self.title

class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, related_name='completions', on_delete=models.CASCADE)
    completed_date = models.DateField()

# --- НОВАЯ МОДЕЛЬ ДЛЯ ВАЖНЫХ ПЛАНОВ ---
class Plan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    date = models.DateField()
    is_important = models.BooleanField(default=True)
    ai_motivation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title