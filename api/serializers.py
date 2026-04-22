from rest_framework import serializers
from .models import Habit, HabitCompletion, Plan

class HabitCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitCompletion
        fields = ['id', 'completed_date']

class HabitSerializer(serializers.ModelSerializer):
    completions = HabitCompletionSerializer(many=True, read_only=True)

    class Meta:
        model = Habit
        fields = ['id', 'title', 'description', 'created_at', 'completions', 'target_daily_count', 'frequency_type', 'days_of_week', 'interval']

# --- ИСПРАВЛЕННЫЙ СЕРИАЛИЗАТОР ПЛАНОВ ---
class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        # Явно перечисляем поля, ИСКЛЮЧАЯ 'user', чтобы DRF не требовал его в POST-запросе
        fields = ['id', 'title', 'date', 'is_important', 'ai_motivation']