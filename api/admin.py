from django.contrib import admin
from .models import Habit, HabitCompletion


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    # Добавили target_daily_count и end_date в список колонок
    list_display = ('id', 'title', 'user', 'target_daily_count', 'created_at')

    # Добавили фильтры сбоку, чтобы было удобно искать
    list_filter = ('user', 'created_at')

    # Поиск по названию
    search_fields = ('title', 'description')


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display = ('id', 'habit', 'completed_date')
    list_filter = ('completed_date', 'habit__user')